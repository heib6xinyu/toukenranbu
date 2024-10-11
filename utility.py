import subprocess
from PIL import Image, ImageChops
import io
import cv2
import numpy as np
import time
import os
from skimage.metrics import structural_similarity as ssim
import pytesseract
from target import Target, TargetManager
from map import Map, MapManager


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

def find_best_match_in_scene(screenshot, targets, threshold=0.8):
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
    

def check_area(screenshot, target, scene, threshold = 0.8):
    target_name = target.tar_name
    target_type = target.tar_type
    target_coords = target.get_coordinates(scene)
    # Load the target template image
    target_path = os.path.join('data', 'screenshot', target_type, f'{target_name}.png')
    template = cv2.imread(target_path, cv2.IMREAD_COLOR)
    # cv2.imshow("Taget", template)
    # cv2.waitKey(0)  # Press any key to close the window
    # cv2.destroyAllWindows()
    # Get the dimensions of the template
    template_height, template_width = template.shape[:2]
    w = target_coords['w']
    h = target_coords['h']
    for (x,y) in target_coords['coordinates']:
        
        region_of_interest = (x, y, w, h)  # Adjust as necessary
        x, y, w, h = region_of_interest
        cropped_region = screenshot[y:y+h, x:x+w]
        # cv2.imshow("Taget", template)
        # cv2.waitKey(0)  # Press any key to close the window
        # cv2.destroyAllWindows()
        # Resize the cropped region to match the template size
        resized_cropped_region = cv2.resize(cropped_region, (template_width, template_height))

        # Perform template matching
        result = cv2.matchTemplate(resized_cropped_region, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # Set a threshold for a match
        if max_val > threshold:
            print(f"Target found {max_val}")
            #found a severe injure. #TODO: develop healing
            return True
        else:
            print(f"No target found {max_val}")
            return False
        

def check_end_pt(screenshot, map, threshold = 0.8):
    best_match_name = None
    best_confidence = 0
    map_name = map.map_name
    stop_coords = map.get_stops()
    # the path is a path to the map directory
    map_path = os.path.join('data', 'map', map_name)
    maps = load_targets(map_path)
    for stop in stop_coords:
        w = stop_coords[stop]['w']
        h = stop_coords[stop]['h']
        [(x,y)] = stop_coords[stop]['coordinates']#for map there will only be one x,y
        for map_name, template_path in maps.items():
            # Load the template image 
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            
            if template is None:
                print(f"Error: Template image at {template_path} could not be loaded.")
                continue
            template_height, template_width = template.shape[:2]
            
            cropped_region = screenshot[y:y+h, x:x+w]
            # cv2.imshow("Taget", cropped_region)
            # cv2.waitKey(0)  # Press any key to close the window
            # cv2.destroyAllWindows()
            # Resize the cropped region to match the template size
            resized_cropped_region = cv2.resize(cropped_region, (template_width, template_height))
            #template_blurred = cv2.GaussianBlur(template, (5, 5), 0)
            
            result = cv2.matchTemplate(resized_cropped_region, template, cv2.TM_CCOEFF_NORMED) 
            # Get the best match position
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(f'target: {map_name} has confidence: {max_val}')
            # Check if the current match is the best one so far
            if max_val > best_confidence and max_val >= threshold:
                best_confidence = max_val
                best_match_name = map_name

    if best_match_name:
        print(f"Best match: {best_match_name} with confidence: {best_confidence}")
        return True, best_confidence
    else:
        print("No good match found.")
        return False, None
    

def crop_from_screenshot():
    # Global variables to store the coordinates
    ref_point = []
    cropping = False

    def click_and_crop(event, x, y, flags, param):
        global ref_point, cropping
        
        # Start recording the initial coordinates when the left mouse button is pressed
        if event == cv2.EVENT_LBUTTONDOWN:
            ref_point = [(x, y)]
            cropping = True

        # Update the second point when the mouse is dragged
        elif event == cv2.EVENT_MOUSEMOVE and cropping:
            # Show the rectangle being drawn
            img_copy = param.copy()
            cv2.rectangle(img_copy, ref_point[0], (x, y), (0, 255, 0), 2)
            cv2.imshow("image", img_copy)

        # Record the endpoint and stop cropping when the left mouse button is released
        elif event == cv2.EVENT_LBUTTONUP:
            ref_point.append((x, y))
            cropping = False
            # Draw the rectangle on the image
            cv2.rectangle(param, ref_point[0], ref_point[1], (0, 255, 0), 2)
            cv2.imshow("image", param)

    def crop_image(image):
        # Load the image and clone it for resetting if needed
        
        clone = image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", click_and_crop, param=clone)

        # Loop until the user hits 'c' to confirm the crop or 'r' to reset
        while True:
            cv2.imshow("image", image)
            key = cv2.waitKey(1) & 0xFF

            # Press 'r' to reset the cropping region
            if key == ord('r'):
                image = clone.copy()

            # Press 'c' to confirm the cropping region
            elif key == ord('c'):
                break

        cv2.destroyAllWindows()

        # Check if the points are valid
        if len(ref_point) == 2:
            # Return the cropped region and the coordinates as x, y, w, h in a dictionary
            x1, y1 = ref_point[0]
            x2, y2 = ref_point[1]
            
            # Calculate width and height
            w = x2 - x1
            h = y2 - y1
            
            # Create the region of interest (ROI)
            roi = clone[y1:y2, x1:x2]
            
            # Return a dictionary with coordinates and dimensions
            return roi, {"coordinates": [(x1, y1)], "w": w, "h": h}
        else:
            print("No valid region selected.")
            return None, None

    screenshot = capture_screenshot()
    cropped_region, coordinates = crop_image(screenshot)

    if cropped_region is not None:
        print(f"Cropped coordinates: {coordinates}")
        cv2.imshow("Cropped Region", cropped_region)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return cropped_region, coordinates