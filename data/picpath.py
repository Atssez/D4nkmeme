import os
import json

# Path to your image folder
image_folder = r"C:\Users\Atsez\Desktop\TelegramBot\data\fshbaitimg"

# Path to your JSON file
json_path = "baits.json"

# Load existing location data
with open(json_path, "r", encoding="utf-8") as f:
    locations = json.load(f)

# Create a mapping of normalized names to image paths
image_map = {}
for filename in os.listdir(image_folder):
    if filename.lower().endswith(".png"):
        name = os.path.splitext(filename)[0].replace("_", " ").lower()
        full_path = os.path.join(image_folder, filename)
        image_map[name] = full_path

# Update JSON with image paths
for loc in locations:
    loc_name = loc["name"].lower()
    if loc_name in image_map:
        loc["link"] = image_map[loc_name]

# Save updated JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(locations, f, indent=4)

print("✅ fish_loc.json updated with image paths.")
