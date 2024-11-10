#%%
import subprocess
from PIL import Image, ImageChops
import io
import cv2
import numpy as np
import time
import os
from skimage.metrics import structural_similarity as ssim
import pytesseract
from utility import *
from march import March
from touken import ToukenManager
import keyboard
# %%
# %%
# setup
connect_adb()
target_manager = TargetManager('data/targets.json')
# Load targets
button_targets = target_manager.load_targets_from_json()
map_manager = MapManager('data/map_target.json')
# Load targets
map_targets = map_manager.load_maps_from_json()

touken_manager = ToukenManager('data/touken.json')
# Load targets
touken_targets = touken_manager.load_toukens_from_json()
#load path
scene_directory = os.path.join('data', 'screenshot','scene')
scene_path = load_targets(scene_directory)

button_directory = os.path.join('data', 'screenshot','button')
button_path = load_targets(button_directory)

status_directory = os.path.join('data', 'screenshot','status')
status_path = load_targets(status_directory)

battlefield_directory = os.path.join('data', 'screenshot','battlefield')
battlefield_path = load_targets(battlefield_directory)
touken_directory = os.path.join('data', 'screenshot','touken')
touken_path = load_targets(touken_directory)
march = March(1,scene_path,battlefield_path,button_path,status_path,touken_path,button_targets,map_targets,touken_targets)


# %%
counter = 0
# %%

while True:
    march.march_ldz()
    counter += 1
    print(f"Run {counter} times.")
    # march.check_state_reconnect()#TODO: arrangement just for now.
    # Break the loop if "q" key is pressed
    if keyboard.is_pressed("z"):
        print("Exiting the loop as 'z' was pressed.")
        break
# %%
counter
# %%
_, coord = crop_from_screenshot()
# %%
screenshot= capture_screenshot()

scene_now, confidence = find_best_match_in_scene(screenshot, scene_path, threshold=0.6)
# %%
march.select_predefine_team(1)
# %%
confirm_num = march.search_injured_char(0.5)
# %%
screenshot_image = capture_screenshot()
# Display the screenshot (optional)
found, num = check_area(screenshot_image, button_targets['severe_injure'],'team_select', threshold=0.6)

# %%
march.healing('taidao',True)
# %%
march.equipt()
# %%
status_path = fr'data\screenshot\status\severe_injure.png'
screenshot= capture_screenshot()
find_template_in_screenshot(screenshot,status_path,0.6)
# %%

# %%
status_path = fr'data\screenshot\button\test_ocr.png'
region = cv2.imread(status_path)
detect_text_from_region(region)
# %%
img = Image.open(status_path)
text = pytesseract.image_to_string(img, lang='chi_sim')
print(text)
# %%

# %%
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
