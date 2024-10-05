#%%
import subprocess
from PIL import Image, ImageChops
import io
import cv2
import numpy as np
import time

# %%
#abd commands
def connect_adb():
    try:
        # Run the adb connect command
        result = subprocess.run(["adb", "connect", "127.0.0.1:16384"], capture_output=True, text=True)

        # Check if the connection was successful and output the result
        if result.returncode == 0:
            print(f"ADB connected successfully: {result.stdout}")
        else:
            print(f"Failed to connect ADB: {result.stderr}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def adb_tap(x, y):
    # Send the tap command to the emulator at the specified coordinates
    subprocess.run(f"adb shell input tap {x} {y}", shell=True)

def adb_swipe(x1, y1, x2, y2, duration):
    """
    Perform an ADB swipe from (x1, y1) to (x2, y2) over the specified duration.
    
    Parameters:
    - x1, y1: Start coordinates of the swipe
    - x2, y2: End coordinates of the swipe
    - duration: Duration of the swipe in milliseconds
    """
    try:
        # Run the adb swipe command
        result = subprocess.run(
            ["adb", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)],
            capture_output=True, text=True
        )
        
        # Check if the command executed successfully
        if result.returncode == 0:
            print(f"Swipe successful: {result.stdout}")
        else:
            print(f"Failed to perform swipe: {result.stderr}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
# %%
def capture_screenshot():
    # Run the adb command and capture the screenshot as raw binary data
    result = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=subprocess.PIPE)
    image_data = result.stdout
    screenshot = Image.open(io.BytesIO(image_data)).convert("RGB")
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot

def find_template_in_screenshot(screenshot, template_path,threshold = 0.7):
    #Load the template image from the local file system
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    # screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    # template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
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
    cv2.imshow("Matched Result", resize_image(screenshot))
    cv2.waitKey(0)
    cv2.destroyAllWindows()    
    if max_val >= threshold:
        print(f"Match found with confidence: {max_val}")
        return top_left, w, h
    else:
        print('No good enough match.')
        print(f"Best confidence: {max_val}")
        return None, None, None


    
def resize_image(image, scale_percent=50):
    # Resize the image to reduce its size
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


# %%
# Example usage
connect_adb()
# %%
screenshot_image = capture_screenshot()

local_image = fr'data\screenshot\button\auto_equipt_valid.png'

# Display the screenshot (optional)
top_left, width, height = find_template_in_screenshot(screenshot_image, local_image)
# %%

for i in range(10000):
    screenshot_image = capture_screenshot()
    top_left, width, height = find_template_in_screenshot(screenshot_image, local_image)


# %%
adb_tap(top_left[0], top_left[1])
# %%
screenshot_image = capture_screenshot()

# Extract text from the button image
