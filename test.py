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
# %%
screenshot= capture_screenshot()
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

# %%

# %%
# %%
target_manager = TargetManager('data/targets.json')

# Load targets
button_targets = target_manager.load_targets_from_json()
button_targets
# %%

# %%
map_manager = MapManager('data/map_target.json')

# Load targets
map_targets = map_manager.load_maps_from_json()
# %%
map_targets['2_3'].get_stops()

# %%
# %%
# Example usage
connect_adb()
# %%
screenshot_image = capture_screenshot()

local_image = fr'data\screenshot\button\add_teammate.png'

# Display the screenshot (optional)
top_left, width, height = find_template_in_screenshot(screenshot_image, local_image)


# %%

# %%

scene_directory = os.path.join('data', 'screenshot','scene')
scene_path = load_targets(scene_directory)
scene_path
# %%
button_directory = os.path.join('data', 'screenshot','button')
button_path = load_targets(button_directory)
button_path
# %%
status_directory = os.path.join('data', 'screenshot','status')
status_path = load_targets(status_directory)
status_path
# %%
battlefield_directory = os.path.join('data', 'screenshot','battlefield')
battlefield_path = load_targets(battlefield_directory)
battlefield_path
# %%
# %%
screenshot= capture_screenshot()
best_target, confidence = find_best_match_in_scene(screenshot, scene_path, threshold=0.6)
# %%
screenshot= capture_screenshot()
best_target, confidence = find_best_match_using_ssim(screenshot, scene_path, threshold=0.8)

# %%
march = March(1,scene_path,battlefield_path,button_path,status_path,button_targets,map_targets)


# %%
march.click3()
# %%
march.clickButton('battle_set_out','march_now')
# %%
march.clickButton('next_step','keep_on')
# %%
screenshot= capture_screenshot()

check_end_pt(screenshot, march.map_target["2_3"],threshold=0.8)
# %%
# %%
march.clickButton('next_step','return_base','go_home')
# %%
march.clickButton('go_home','yes','home')

# %%

# %%

                
# %%
march.march("5_4",False,False,1)
# %%
