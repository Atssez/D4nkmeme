import os
import json
import requests
from PIL import Image
from io import BytesIO
import re

# Create folder if it doesn't exist
os.makedirs("fshlocimg", exist_ok=True)

# Normalize filename
def normalize_filename(name):
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_') + ".png"

# Load fishing tools JSON
with open("fish_loc.json", "r", encoding="utf-8") as f:
    tools = json.load(f)

for tool in tools:
    name = tool.get("name")
    link = tool.get("link")

    if not name or not link:
        print(f"Skipping: Missing name or link for tool: {tool}")
        continue

    try:
        response = requests.get(link, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")

        filename = normalize_filename(name)
        filepath = os.path.join("fshlocimg", filename)

        if "gif" in content_type:
            # Convert GIF to PNG
            gif = Image.open(BytesIO(response.content))
            gif.convert("RGBA").save(filepath, "PNG")
            print(f"Converted GIF to PNG: {filename}")
        elif "png" in content_type:
            # Save PNG directly
            with open(filepath, "wb") as out_file:
                out_file.write(response.content)
            print(f"Saved PNG: {filename}")
        else:
            print(f"Unsupported format for {name}: {content_type}")

    except Exception as e:
        print(f"Error downloading {name}: {e}")
