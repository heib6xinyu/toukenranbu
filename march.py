from utility import *
class March:
    def __init__(self, team, scene_path, battlefield_path, button_path, status_path, button_targets, map_targets):
        self.team = team
        self.scene_path = scene_path  # Dictionary of path to scenes
        self.battlefield_path = battlefield_path  # Dictionary of path to battlefields
        self.button_path = button_path  # Dictionary of path to buttons
        self.status_path = status_path  # Dictionary of path to status
        self.button_targets = button_targets #dimension info for buttons
        self.map_targets = map_targets #dimension info for maps
        self.state = None

    def click1(self):
        adb_tap(438, 594)
        return True
    def click2(self):
        adb_tap(962, 601)
        return True
    def click3(self):
        adb_tap(438, 809)
        return True
    def click4(self):
        adb_tap(962, 834)
        return True
    def click_random(self):
        adb_tap(944,313)
        return True

    
    #2. usually by default it's the first team showing
    #3. 
    def select_char(self, who, healing):
        screenshot = capture_screenshot()
        matched, _ = self.match_scene(screenshot,self.scene_path['home'],threshold=0.8)
        
        if matched:
            #1. from home click team button
            clicked = self.clickButton('home','team_button')
            if clicked:

                clicked = self.clickButton('healing_team',)
            else:
                print('Team_button not found.')
                return False
        else:
            print('Not Starting at home')
            return False

        
    def clickButton(self, start_scene, button):
        # screenshot= capture_screenshot()
        # matched, confidence = match_scene(screenshot, self.scene_path[start_scene], threshold=0.7)
        # if matched:
        screenshot= capture_screenshot()
        wanted_button = check_area(screenshot, self.button_targets[button], start_scene,threshold=0.5)
        if wanted_button:
            #found march image
            coords = self.button_targets[button].get_coordinates(start_scene)
            [(x,y)] = coords['coordinates']
            w = coords['w']
            h = coords['h']
            middle_x = w // 2
            middle_y = h // 2
            
            adb_tap(x+middle_x, y+middle_y)
            return True
        else:
            print(f'Not wanted button {button}')
            return False
        # else:
        #     print('Not wanted start_scene')
        #     return False

    def match_scene(self, screenshot, scene_template, threshold=0.8):
        """
        Compare multiple target templates to the current screenshot and return the name of the target with the highest confidence.
        
        Parameters:
        - screenshot: The current screenshot (OpenCV image).
        - scene_template: path to the scene_template.
        - threshold: Matching threshold (0-1). A higher value means a more exact match is required.
        
        Returns:
        - match: boolean of whether it is a match
        - max_val: Confidence score of the match.
        """
        

        template = cv2.imread(scene_template, cv2.IMREAD_COLOR)
        
        if template is None:
            print(f"Error: Template image at {scene_template} could not be loaded.")
            return False, None
        else:
            screenshot_blurred = cv2.GaussianBlur(screenshot, (5, 5), 0)
            template_blurred = cv2.GaussianBlur(template, (5, 5), 0)
            result = cv2.matchTemplate(screenshot_blurred, template_blurred, cv2.TM_CCOEFF_NORMED) 
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if  max_val >= threshold:
                print(f"Match found for {scene_template}, confidence {max_val}.")
                return True, max_val
        print(f"No match for {scene_template}, confidence {max_val}.")
        return False, None

    def wait_for_scene(self, scene, speed):
        '''
        Helper function, wait to see if the screen is scene, return boolean
        
        Parameters:
        - scene: scene to be matched 

        Return:
        - boolean
        '''
        while True:
            self.click_random()
            time.sleep(speed)
            screenshot = capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path["severe_injure_warning1"], threshold=0.7)  
            if matched:
                return True
            


    def injury_check_in_battle(self, speed):
        #return if someone is injured
        #8. check severe_injure warning 1&2
        while True:
            self.click_random()
            time.sleep(speed)
            screenshot = capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path["severe_injure_warning1"], threshold=0.7)  
            if matched:
                #8-1. if so, click no
                clicked = self.clickButton('severe_injure_warning1','no')
                while clicked:
                    time.sleep(speed)
                    screenshot= capture_screenshot()
                    
                    matched, confidence = self.match_scene(screenshot, self.scene_path['next_step'], threshold=0.7)
                    if matched:
                        break
                at_home = self.go_home(speed)
                return at_home
            else:
                matched, confidence = self.match_scene(screenshot, self.scene_path["next_step"], threshold=0.7)
                if matched:
                    #no one injured.
                    break
            screenshot = capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path["home"], threshold=0.7)  
            if matched:
                print("Successfully runned once, keep going")
                break
        return False

    def go_home(self, speed):
        clicked = self.clickButton('next_step','return_base')
        while clicked:
            time.sleep(speed)
            screenshot= capture_screenshot()
            
            matched, confidence = self.match_scene(screenshot, self.scene_path['go_home'], threshold=0.7)
            if matched:
                break
        #6-2. click yes
        clicked = self.clickButton('go_home','yes')
        while clicked:
            time.sleep(speed)
            screenshot= capture_screenshot()
            
            matched, confidence = self.match_scene(screenshot, self.scene_path['home'], threshold=0.7)
            if matched:
                break
        return True
    
    
    #try a full cycle
    #1. from home click march button
    #2. from march_page click march image
    #3. TODO select era click era
    #4. TODO select location click location
    #5. from battle_set_out click march_now
        #5-1. from possible severe_injure_warning1, click no
        
    # REPEAT START (random clicking on buttonless area TODO)
    #6. from next_step check_stop_pt
        #6-1. if stop, click return_base
        #6-2. click yes
    #7. from next_step click keep_on
    #8. check severe_injure warning 1&2
        #8-1. if so, click return_base
        #8-2. click yes
        #8-3. check if at home, END REPEAT
    #9. TODO implement healing
    #10. END REPEAT, START AGAIN.
    
        

    def march(self, map_name, stop_before_boss, healing, speed):
        """
        Compare multiple target templates to the current screenshot and return the name of the target with the highest confidence.
        
        Parameters:
        - screenshot: The current screenshot (OpenCV image).
        - target: path to the target_template.
        - threshold: Matching threshold (0-1). A higher value means a more exact match is required.
        
        Returns:
        - again: boolean of whether to keep marching the same map
        
        """
        screenshot= capture_screenshot()
        at_home, confidence = self.match_scene(screenshot, self.scene_path['home'], threshold=0.7)
        if not at_home:
            print("Not starting at home.")
            return False
        #1. from home click march button
        clicked = self.clickButton('home','march_button')
        while clicked:
            time.sleep(speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['march_page'], threshold=0.8)
            if matched:
                break
        #2. from march_page click march image
        clicked = self.clickButton('march_page','march_image')
        while clicked:
            time.sleep(speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['battlefield_select'], threshold=0.8)
            if matched:
                break
        #3. TODO select era click era
        #4. TODO select location click location
        
        #so far default select l3, so far I will assume
        #the l3 click position is the safe default click(only when in battle)
        clicked = self.click3()
        while clicked:
            time.sleep(speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['battle_set_out'], threshold=0.8)
            if matched:
                break
        #5. from battle_set_out click march_now
        clicked = self.clickButton('battle_set_out','march_now')
        while clicked:
            time.sleep(speed)
            screenshot= capture_screenshot()
            
            matched, confidence = self.match_scene(screenshot, self.scene_path['severe_injure_warning1'], threshold=0.7)
            if matched:
                if healing and map_name == '1_1':
                    #this is a 1-1 healing trip
                    healing()
                else:
                    #5-1. from possible severe_injure_warning1, click no
                    clicked = self.clickButton('severe_injure_warning1','no')
                    while clicked:
                        time.sleep(speed)
                        screenshot= capture_screenshot()
                        
                        matched, confidence = self.match_scene(screenshot, self.scene_path['battle_set_out'], threshold=0.7)
                        if matched:
                            break
                    clicked = self.clickButton('battle_set_out','home_button')
                    while clicked:
                        time.sleep(speed)
                        screenshot= capture_screenshot()
                        
                        matched, confidence = self.match_scene(screenshot, self.scene_path['home'], threshold=0.7)
                        if matched:
                            break
                    print('Someone severely injured, stop.')
                    return False
            matched, confidence = self.match_scene(screenshot, self.battlefield_path[map_name], threshold=0.7)
            if matched:
                #If matched, start the map
                print(f"start marching {map_name}...")
                break
        #REPEAT START
        #6. from next_step check_end_pt
        
        while True:
            self.click_random()
            time.sleep(speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path["next_step"], threshold=0.7)
            if matched:
                #6-1. if stop, click return_base
                #screenshot= capture_screenshot()
                if stop_before_boss:
                    found_stop, _ =check_end_pt(screenshot, self.map_targets[map_name],threshold=0.78)
                    if found_stop:
                        at_home = self.go_home(speed)
                        if at_home:
                            print("Successfully runned once, keep going.")
                            return True
                    #not at stop yet
                    clicked = self.clickButton('next_step','keep_on')
                    injury = self.injury_check_in_battle(speed)
                    if injury:
                        print('Someone severely injured, stop.')
                        return False
                else:
                    #no need to stop before boss
                    clicked = self.clickButton('next_step','keep_on')
                    #8. check severe_injure warning 1&2
                    injury = self.injury_check_in_battle(speed)
                    if injury:
                        print('Someone severely injured, stop.')
                        return False
            
        
