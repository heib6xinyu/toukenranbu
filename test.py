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

def find_template_in_screenshot(screenshot, template_path,threshold = 0.3):
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
    cv2.waitKey(5000)
    cv2.destroyAllWindows()    
    if max_val >= threshold:
        print(f"Match found with confidence: {max_val}")
        return top_left, w, h
    else:
        print('No good enough match.')
        print(f"Best confidence: {max_val}")
        return None, None, None

def find_best_match_in_scene(screenshot, targets, threshold=0.3):
    """
    Compare multiple target templates to the current screenshot and return the name of the target with the highest confidence.
    
    Parameters:
    - screenshot: The current screenshot (OpenCV image).
    - targets: A dictionary where keys are target names and values are paths to template images.
    - threshold: Matching threshold (0-1). A higher value means a more exact match is required.
    
    Returns:
    - best_match_name: Name of the target with the highest confidence match.
    - best_confidence: Confidence score of the best match.
    """
    best_match_name = None
    best_confidence = 0
    
    for target_name, template_path in targets.items():
        # Load the template image (full screen)
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        
        if template is None:
            print(f"Error: Template image at {template_path} could not be loaded.")
            continue


        screenshot_blurred = cv2.GaussianBlur(screenshot, (5, 5), 0)
        template_blurred = cv2.GaussianBlur(template, (5, 5), 0)
        result = cv2.matchTemplate(screenshot_blurred, template_blurred, cv2.TM_CCOEFF_NORMED) 
        # Get the best match position
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(f'target: {target_name} has confidence: {max_val}')
        # Check if the current match is the best one so far
        if max_val > best_confidence and max_val >= threshold:
            best_confidence = max_val
            best_match_name = target_name

    if best_match_name:
        print(f"Best match: {best_match_name} with confidence: {best_confidence}")
        return best_match_name, best_confidence
    else:
        print("No good match found.")
        return None, None

def compare_images_ssim(imageA, imageB):
    """
    Compare two images using SSIM (Structural Similarity Index) and return the similarity score.
    """
    # Convert images to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    
    # Compute SSIM between the two images
    score, _ = ssim(grayA, grayB, full=True)
    
    return score

def find_best_match_using_ssim(screenshot, targets, threshold=0.3):
    """
    Compare multiple full-screen target templates to the current screenshot using SSIM and return the name of the target with the highest score.
    """
    best_match_name = None
    best_score = 0

    for target_name, template_path in targets.items():
        # Load the template image
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        
        if template is None:
            print(f"Error: Template image at {template_path} could not be loaded.")
            continue

        # Compare the screenshot and template using SSIM
        score = compare_images_ssim(screenshot, template)
        print(f'target: {target_name} has confidence: {score}')

        # Update best match if this score is higher than the previous best
        if score > best_score and score >= threshold:
            best_score = score
            best_match_name = target_name

    if best_match_name:
        print(f"Best match: {best_match_name} with SSIM score: {best_score}")
        return best_match_name, best_score
    else:
        print("No good match found.")
        return None, None
    
def load_targets(directory):
    """
    Automatically loads all target templates from the specified directory.
    
    Parameters:
    - directory: Path to the directory containing the target template images.
    
    Returns:
    - targets: A dictionary where the keys are target names (from filenames) and values are the file paths.
    """
    targets = {}
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):  # Accept common image formats
            target_name = os.path.splitext(filename)[0]  # Get the name without the extension
            file_path = os.path.join(directory, filename)  # Full path to the file
            targets[target_name] = file_path
    return targets


def non_max_suppression(boxes, overlap_threshold=0.5):
    if len(boxes) == 0:
        return []

    boxes = np.array(boxes)
    pick = []

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 0] + boxes[:, 2]
    y2 = boxes[:, 1] + boxes[:, 3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]

        idxs = np.delete(
            idxs, np.concatenate(([last], np.where(overlap > overlap_threshold)[0]))
        )

    return boxes[pick].astype(int)


def find_all_matching_regions(image, template_path, threshold=0.8,overlap_threshold=0.5):
    """
    Find all regions in the image that match the template with a confidence above the threshold.
    Draw rectangles around them for debugging.
    
    Returns:
    - List of top-left corners of matched regions.
    """
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    # screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    # template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # Perform template matching
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    # Find locations where confidence is above the threshold
    locations = np.where(result >= threshold)

    # Get the template dimensions
    h, w = template.shape[:2]

    # Create a list of all matches including their coordinates and size (x, y, w, h)
    matching_regions = [(pt[0], pt[1], w, h) for pt in zip(*locations[::-1])]

    # Apply non-max suppression to filter overlapping regions
    filtered_boxes = non_max_suppression(np.array(matching_regions), overlap_threshold)

    # Draw rectangles around the filtered matching regions
    for (x, y, w, h) in filtered_boxes:
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)  # Draw a green rectangle
        print(f'found box at {top_left}, {bottom_right}')

    # Display the image with rectangles
    cv2.imshow("Matching Regions", resize_image(image))
    cv2.waitKey(0)  # Press any key to close the window
    cv2.destroyAllWindows()

    
    return filtered_boxes

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

local_image = fr'data\screenshot\status\severe_injure.png'

# Display the screenshot (optional)
top_left, width, height = find_template_in_screenshot(screenshot_image, local_image)

# %%
adb_tap(top_left[0], top_left[1])
# %%

target_directory = os.path.join('data', 'screenshot','scene')
targets = load_targets(target_directory)
targets
# %%
screenshot= capture_screenshot()
best_target, confidence = find_best_match_in_scene(screenshot, targets, threshold=0.8)
# %%
screenshot= capture_screenshot()
best_target, confidence = find_best_match_using_ssim(screenshot, targets, threshold=0.8)
# %%
button_target_directory = os.path.join('data', 'screenshot','button')
button_targets = load_targets(button_target_directory)
button_targets
# %%
status_target_directory = os.path.join('data', 'screenshot','status')
status_targets = load_targets(status_target_directory)
status_targets
# %%
#test cycle
#1. check scene
#2. find button
#3. click button
#4. check scene to make sure it is correct
def clickButton(start_scene, button, end_scene):
    screenshot= capture_screenshot()
    best_target, confidence = find_best_match_in_scene(screenshot, targets, threshold=0.7)
    if best_target == start_scene:
        screenshot= capture_screenshot()
        # check status first
        injure = check_status(screenshot,status_targets['severe_injure'])
        # is there anyone severe injured
        if injure:
            top_left, width, height = find_template_in_screenshot(screenshot, button_targets['return_base'])
            adb_tap(top_left[0], top_left[1])
            time.sleep(2)#TODO: implement wait until
            print('someone injured, go home')
            return False
        top_left, width, height = find_template_in_screenshot(screenshot, button_targets[button])
        adb_tap(top_left[0], top_left[1])
        time.sleep(2)#TODO: implement wait until
        screenshot= capture_screenshot()
        best_target, confidence = find_best_match_in_scene(screenshot, targets, threshold=0.8)
        if best_target == end_scene:
            print('success')
            return True
        else:
            print('ends up in wrong place')
            return False
    else:
        print('start at wrong place')
        return False
# %%
clickButton('home','march_button','march_page')
# %%
clickButton('march_page','march_image','battlefield_select')
# %%
clickButton('next_step','keep_on','battlefield')
# %%
def check_status(screenshot, status, threshold = 0.4):
    top_left, width, height = find_template_in_screenshot(screenshot, status)
    if top_left:
        return True
    else:
        return False
# %%
status_path = fr'data\screenshot\status\severe_injure.png'

screenshot= capture_screenshot()
check_status(screenshot,local_image)
# %%
def detect_text_from_region(region):
    """
    Use OCR to detect text from a single region.
    
    Parameters:
    - region: The cropped region's coordinate.
    
    Returns:
    - detected_text or None.
    """
    #matched_region = screenshot[region[1]:region[1] + region[3], region[0]:region[0] + region[2]]
        
    # Convert the matched region to grayscale for better OCR results
    gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    
    #blurred_image = cv2.GaussianBlur(gray_region, (5, 5), 0)
    _, binary_image = cv2.threshold(gray_region, 150, 255, cv2.THRESH_BINARY)
    cv2.imshow("Matching Regions", binary_image)
    cv2.waitKey(0)  # Press any key to close the window
    cv2.destroyAllWindows()
    # Perform OCR on the region (assuming Chinese Simplified for injury levels)
    detected_text = pytesseract.image_to_string(binary_image, lang='chi_sim')
    

    if detected_text.strip():  # Only return non-empty results
        print(f"Detected text: {detected_text.strip()}")
        return detected_text.strip()
    else:
        print("No text detected in this region.")
        return None
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
matching_regions = find_all_matching_regions(screenshot, status_path, threshold=0.3)
# %%
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# %%
template = cv2.imread(status_path)

for box in matching_regions:
    # Define the region where the template was found (use the template size)
    detect_text_from_region(box)
    

