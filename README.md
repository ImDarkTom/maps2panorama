# maps2panorama

Create Minecraft panorama resource packs using the [Google Maps Street View Static API](https://developers.google.com/maps/documentation/streetview/overview).

## Overview

`maps2panorama` fetches a Google Maps street view panorama as a cubemap, and packages it into a valid Minecraft 1.21+ resource pack ZIP file.


## Installation & Running

### Prerequisites

- **A valid Google Maps Platform API Key**
- **Python 3.12+**
- **Git**

### 1. Clone the repository

```bash
git clone https://github.com/ImDarkTom/maps2panorama
cd maps2panorama
```

### 2. Create and activate virtual environment

Create the virtual environment:

```bash
python -m venv venv
```

Activate it:

#### Windows:

```bash
.\venv\Scripts\activate
```

#### Linux/MacOS:

```bash
source ./venv/bin/activate
```

> You should see `(venv)` in your terminal once it's activated.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python main.py
```

> Once started, if everything installed correctly, you'll be prompted to enter a location in the terminal.

## License

maps2panorama is [AGPL-3.0](https://github.com/ImDarkTom/maps2panorama/blob/main/LICENSE)