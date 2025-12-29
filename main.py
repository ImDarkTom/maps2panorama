import os
import requests
import uuid
import shutil
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

ROOT_PATH = Path(__file__).parent

API_KEY = os.getenv("API_KEY")
FOV = 90
IMAGE_SIZE="1024x1024"

SIDES = {
    'panorama_0': (0, 0), # front 
    'panorama_1': (90, 0), # right
    'panorama_2': (180, 0), # back
    'panorama_3': (270, 0), # left
    'panorama_4': (0, 90), # up
    'panorama_5': (0, -90) # down
}

def get_abs_path(path: str) -> str:
    """
    Prepend the script's path to a given folder name.
    
    :param path: Path to get absolute of.
    :type path: str
    :return: The absolute path of the folder.
    :rtype: str
    """
    return os.path.join(ROOT_PATH, path)

def create_temp_dir() -> str:
    """
    Creates a unique temporary directory.
    
    :return: The created folder name.
    :rtype: str
    """
    temp_dir = os.path.join("temp_" + uuid.uuid4().hex[:8])
    os.makedirs(temp_dir, exist_ok=True)

    return temp_dir

def convert_jpgs_to_pngs(directory: str):
    """
    Converts all jpg files into png files within a specified directory.
    
    :param directory: The in which to scan and convert files in.
    :type directory: str
    """
    for filename in os.listdir(directory):
        if filename.lower().endswith(".jpg"):
            jpg_path = os.path.join(directory, filename)
            png_path = os.path.join(directory, os.path.splitext(filename)[0] + ".png")

            with Image.open(jpg_path) as img:
                img.save(png_path, "PNG")

            os.remove(jpg_path)

def create_pack(description: str, image_dir: str) -> str:
    """
    Create the resource pack.
    
    :param description: Description to show up in-game under the filename in the resource pack list.
    :type description: str
    :param image_dir: The directory from which to copy the panorama files from.
    :type image_dir: str
    :return: The absolute path of the created resource pack folder.
    :rtype: str
    """

    pack_dir = create_temp_dir()

    os.makedirs(os.path.join(ROOT_PATH, f"{pack_dir}/assets/minecraft/textures/gui/title/background".lstrip("/")), exist_ok=True)

    with open(os.path.join(ROOT_PATH, pack_dir, 'pack.mcmeta'), 'w') as f:
        f.write(f'{{"pack": {{"pack_format": 34,"min_format": 1,"max_format": 75,"supported_formats": {{"min_inclusive": 1, "max_inclusive": 75}},"description": "{description}"}}}}')

    dest_dir = os.path.join(ROOT_PATH, pack_dir, 'assets', 'minecraft', 'textures', 'gui', 'title', 'background')

    for filename in os.listdir(image_dir):
        src_path = os.path.join(image_dir, filename)
        dst_path = os.path.join(dest_dir, filename)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)

    shutil.rmtree(image_dir)

    return get_abs_path(pack_dir)


def fetch_streetview_images(location: str) -> str:
    """
    Fetch streetview images for a given location in cube map format.
    
    :param location: The location, can be actual name or coordinate, anything the Google Maps API accepts.
    :type location: str
    :return: The absolute path of a folder containing the streetview images in cube map format.
    :rtype: str
    """

    temp_dir = create_temp_dir()

    for name, (heading, pitch) in SIDES.items():
        url = f"https://maps.googleapis.com/maps/api/streetview?size={IMAGE_SIZE}&location={location}&fov={FOV}&heading={heading}&pitch={pitch}&key={API_KEY}"
        response = requests.get(url)

        path = os.path.join(temp_dir, f"{name}.jpg")
        with open(path, 'wb') as f:
            f.write(response.content)

    convert_jpgs_to_pngs(temp_dir)

    return get_abs_path(temp_dir)

def map2panorama(location: str, pack_name: str, description: str):
    image_dir = fetch_streetview_images(location)

    created_pack_dir = create_pack(description, image_dir)

    shutil.make_archive(pack_name, 'zip', created_pack_dir)
    shutil.rmtree(created_pack_dir)

    print(f'Saved to \'{pack_name}.zip\'!')

if __name__ == "__main__":
    location = input("Enter location, this can be a name e.g. 'New York', or coordinates e.g. '29.315311813357592, 110.43475099921915': ")
    pack_name = input("Enter the pack/zip file name: ")
    description = input("Enter pack description (in-game text) (can be blank): ")

    map2panorama(location, pack_name, description)