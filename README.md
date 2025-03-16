# Automated Game Control System

This project is a Python-based automated control system designed to manage repetitive tasks in a mobile game. It leverages **ADB (Android Debug Bridge)**, **computer vision**, and **template matching** to automate gameplay actions. It provides functionality to interact with a mobile emulator or a connected Android device, including taking screenshots, detecting scenes, buttons, and performing actions like taps, swipes, and navigation through the game's various tasks and states.

---
## Fully Automated Game Tasks:
以下功能全部包括重伤检测和治疗。
### 1. **地下城**
### 2. **联队战**
### 3. **战力扩充**
### 4. **普通地图重复刷**
- 王点撤退（正在开发）

## Features

### 1. **Automated Gameplay Actions**
- Automates tasks such as healing, team formation, battlefield navigation, and returning home.
- Handles repetitive gameplay elements with minimal user intervention.

### 2. **Scene and Button Detection**
- Detects specific game scenes using **template matching** and **image processing** techniques.
- Identifies and clicks buttons by matching their templates with the current screen.

### 3. **Task State Tracking** (ONGOING)
- Tracks the current state of a task (e.g., healing, marching, fighting) and ensures actions proceed logically.
- Automatically resumes tasks in case of interruptions or errors like timeouts.

### 4. **Error Handling**
- Implements custom error classes (e.g., `SceneTimeoutError`, `ButtonNotFoundError`) to handle unexpected scenarios like connection loss or failed detections.
- Provides error messages to debug and recover from issues.

### 5. **Screen Interaction**
- Captures screenshots from the emulator or connected device using **ADB**.
- Crops specific regions for analysis and interaction.
- Simulates touch interactions using **ADB commands** (`tap`, `swipe`).

### 6. **Template Matching**
- Uses OpenCV's template matching to detect buttons, scenes, and other visual elements on the screen.
- Provides confidence levels for matches and supports retries for better accuracy.

### 7. **Task Modularization**
- Breaks down tasks into smaller, manageable actions (e.g., selecting a battlefield, fighting, moving to the next step).
- Each action is performed in a structured sequence, allowing for easier debugging and customization.

### 8. **Extendable Design**
- Supports adding new tasks, scenes, or buttons dynamically via configuration files.
- Plans for a GUI-based front-end to make the tool more user-friendly.

---

## Installation

### Prerequisites
1. **Python 3.8+**
2. **ADB (Android Debug Bridge):**
   - Ensure ADB is installed and added to your system's PATH.
   - For MuMu Player or other emulators, verify the correct ADB port (e.g., `127.0.0.1:5555`).
3. **Python Libraries:**
   Install the required dependencies using:
   ```bash
   pip install -r requirements.txt
4. **Tesseract OCR (Optional):**
   - For text recognition in certain game states, install Tesseract OCR and ensure it's in your system's PATH.
   - Download the `chi_sim` trained data for Chinese Simplified OCR and place it in the `tessdata` folder.
   - So far the project haven't actually utilized OCR.
### Usage
1. Run the Automation Script: Use Jupyter notebook to run the while loop in test.py, change the function name if needed.

## Key Functionalities

### 1. **ADB Integration**
   - Automates in-game interactions such as tapping, swiping, and capturing screenshots using ADB commands.
   - Example functionalities:
     - **Tap Command:** Simulates a tap gesture on the emulator.
     - **Swipe Command:** Automates swiping actions with customizable duration and direction.
     - **Screenshot Capture:** Captures the current screen for processing.

### 2. **Template Matching with OpenCV**
   - Identifies specific in-game elements or states using template images.
   - Implements dynamic thresholding for accurate matching across varying game states.
   - Features non-max suppression to filter overlapping regions.

### 3. **Dynamic State Tracking**
   - Tracks the progression of multi-step tasks.
   - Allows resumption from the last successful step after an interruption or timeout.
   - Maintains an error log for better debugging and recovery.

### 4. **Error Handling**
   - Introduces robust timeout mechanisms for scene transitions.
   - Handles exceptions gracefully to ensure the program can resume or terminate without crashing.

### 5. **OCR with Tesseract (Optional)**
   - Recognizes on-screen text in specific game states.
   - Utilizes Tesseract OCR with support for Chinese Simplified (`chi_sim`).
   - Includes preprocessing techniques (e.g., grayscale conversion, thresholding) to improve OCR accuracy.

### 6. **JSON-based Configuration**
   - Stores information about targets (e.g., coordinates, dimensions, and associated templates) in JSON files.
   - Facilitates easy updates or additions to target configurations without modifying code.

### 7. **Future GUI Integration**
   - Plans to introduce a graphical user interface for better usability.
   - Intends to convert the application into a runnable executable file for broader accessibility.


## Contribution
Contributors:

[heib6xinyu]: Developer, designer, and tester of the system.

Feel free to fork the project and submit pull requests for enhancements or bug fixes.

## Disclaimer

This project is for educational purposes only. Use responsibly and ensure compliance with the terms of the game or platform.
