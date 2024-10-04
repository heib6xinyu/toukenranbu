#%%
import subprocess
from PIL import Image, ImageChops
import io
import cv2
import numpy as np
# %%
#abd commands
def adb_tap(x, y):
    # Send the tap command to the emulator at the specified coordinates
    subprocess.run(f"adb shell input tap {x} {y}", shell=True)
# %%
def capture_screenshot():
    # Run the adb command and capture the screenshot as raw binary data
    result = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=subprocess.PIPE)
    image_data = result.stdout
    screenshot = Image.open(io.BytesIO(image_data)).convert("RGB")
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot

def find_template_in_screenshot(screenshot, template_path):
    # Load the template image from the local file system
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    
    # Perform template matching
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    
    # Get the best match position
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Define the rectangle's bottom-right corner based on the template size
    h, w = template.shape[:2]
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # Draw a rectangle around the matched region
    cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
    
    # Display the result
    cv2.imshow("Matched Result", screenshot)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return top_left, w, h
# %%
# Example usage
screenshot_image = capture_screenshot()

local_image = r'data\test\keep_marching.png'
# Display the screenshot (optional)
top_left, width, height = find_template_in_screenshot(screenshot_image, local_image)

# %%
adb_tap(top_left[0], top_left[1])