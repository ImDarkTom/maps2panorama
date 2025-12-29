import os
import uuid
import shutil
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image

# --------------------------------------------------
# Config
# --------------------------------------------------

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

PANORAMA_PATH = Path("assets/minecraft/textures/gui/title/background")

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def create_temp_dir() -> Path:
    """
    Creates a unique temporary directory.
    
    :return: The created folder.
    :rtype: Path
    """

    path = ROOT_PATH / f"temp_{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=True)
    return path



def convert_jpgs_to_pngs(directory: Path) -> None:
    """
    Converts all jpg files into png files within a specified directory.
    
    :param directory: The in which to scan and convert files in.
    :type directory: Path
    """

    for jpg in directory.glob("*.jpg"):
        png = jpg.with_suffix(".png")
        with Image.open(jpg) as img:
            img.save(png, "PNG")
        
        # Delete old jpg file
        jpg.unlink()



# --------------------------------------------------
# Core logic
# --------------------------------------------------

def fetch_streetview_images(location: str) -> Path:
    """
    Fetch streetview images for a given location in cube map format.
    
    :param location: The location, can be actual name or coordinate, anything the Google Maps API accepts.
    :type location: str
    :return: Path to folder containing the streetview images in cube map format.
    :rtype: Path
    """

    temp_dir = create_temp_dir()

    for name, (heading, pitch) in SIDES.items():
        url = (
            "https://maps.googleapis.com/maps/api/streetview"
            f"?size={IMAGE_SIZE}"
            f"&location={location}"
            f"&fov={FOV}"
            f"&heading={heading}"
            f"&pitch={pitch}"
            f"&key={API_KEY}"
        )
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        (temp_dir / f"{name}.jpg").write_bytes(response.content)

    convert_jpgs_to_pngs(temp_dir)
    return temp_dir



def create_pack(description: str, image_dir: Path) -> Path:
    """
    Create the resource pack.
    
    :param description: Description to show up in-game under the filename in the resource pack list.
    :type description: str
    :param image_dir: The directory from which to copy the panorama files from.
    :type image_dir: Path
    :return: The absolute path of the created resource pack folder.
    :rtype: str
    """

    pack_dir = create_temp_dir()
    target_dir = pack_dir / PANORAMA_PATH
    target_dir.mkdir(parents=True, exist_ok=True)

    mcmeta = {
        "pack": {
            "pack_format": 34,
            "min_format": 1,
            "max_format": 75,
            "supported_formats": {
                "min_inclusive": 1, 
                "max_inclusive": 75
            },
            "description": description
        }
    }

    # Create mcmeta file
    (pack_dir / "pack.mcmeta").write_text(
        str(mcmeta).replace("'", '"'),
        encoding="utf-8"
    )

    for img in image_dir.iterdir():
        if img.is_file():
            shutil.copy2(img, target_dir / img.name)
    
    # Delete original temporary image dir
    shutil.rmtree(image_dir)

    return pack_dir



def map2panorama(location: str, pack_name: str, description: str):
    image_dir = fetch_streetview_images(location)
    pack_dir = create_pack(description, image_dir)

    shutil.make_archive(pack_name, 'zip', pack_dir)
    shutil.rmtree(pack_dir)

    print(f'Saved to \'{pack_name}.zip\'!')


# --------------------------------------------------
# CLI
# --------------------------------------------------

if __name__ == "__main__":
    location = input("Enter location, this can be a name e.g. 'New York', or coordinates e.g. '29.315311813357592, 110.43475099921915': ")
    pack_name = input("Enter the pack/zip file name: ")
    description = input("Enter pack description (in-game text) (can be blank): ")

    map2panorama(location, pack_name, description)