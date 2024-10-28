from utility import *
class March:
    def __init__(self, team, scene_path, battlefield_path, button_path, status_path, button_targets, map_targets, timeout = 60, speed = 3):
        self.team = team
        self.scene_path = scene_path  # Dictionary of path to scenes
        self.battlefield_path = battlefield_path  # Dictionary of path to battlefields
        self.button_path = button_path  # Dictionary of path to buttons
        self.status_path = status_path  # Dictionary of path to status
        self.button_targets = button_targets #dimension info for buttons
        self.map_targets = map_targets #dimension info for maps
        self.state = None
        self.timeout = timeout
        self.speed = speed

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
    def click_x_y(self,x,y):
        adb_tap(x,y)
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

        
    def clickButton(self, start_scene, button, num = 0, threshold=0.5):
        screenshot= capture_screenshot()
        wanted_button = check_area(screenshot, self.button_targets[button], start_scene, num, threshold)
        if wanted_button:
            #at start scene found wanted button
            coords = self.button_targets[button].get_coordinates(start_scene)
            x,y = coords['coordinates'][num]
            
            w = coords['w']
            h = coords['h']
            middle_x = w // 2
            middle_y = h // 2
            
            adb_tap(x+middle_x, y+middle_y)
            return True
        else:
            print(f'Not wanted button {button} at {start_scene}')
            return False
        

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

    def wait_for_scene(self, scene, threshold = 0.8):
        '''
        Helper function, wait to see if the screen is scene, return boolean
        
        Parameters:
        - scene: scene to be matched 

        Return:
        - boolean
        '''
        start_time = time.time()
        while True:
            self.click_random()
            time.sleep(self.speed)
            screenshot = capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path[scene], threshold)  
            if matched:
                return True
            elapsed_time = time.time() - start_time
            if elapsed_time > self.timeout:
                print(f"Waiting for scene {scene}, timeout. End task.")
                return False
            


    def injury_check_in_battle(self):
        #return if someone is injured
        #8. check severe_injure warning 1&2
        while True:
            self.click_random()
            time.sleep(self.speed)
            screenshot = capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path["severe_injure_warning1"], threshold=0.7)  
            if matched:
                #8-1. if so, click no
                clicked = self.clickButton('severe_injure_warning1','no')
                while clicked:
                    time.sleep(self.speed)
                    screenshot= capture_screenshot()
                    
                    matched, confidence = self.match_scene(screenshot, self.scene_path['next_step'], threshold=0.7)
                    if matched:
                        break
                at_home = self.go_home()
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

    def go_home(self):
        clicked = self.clickButton('next_step','return_base')
        while clicked:
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            
            matched, confidence = self.match_scene(screenshot, self.scene_path['go_home'], threshold=0.7)
            if matched:
                break
        #6-2. click yes
        clicked = self.clickButton('go_home','yes')
        while clicked:
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            
            matched, confidence = self.match_scene(screenshot, self.scene_path['home'], threshold=0.7)
            if matched:
                break
        return True
    
    def home_to_battle_select(self):
        screenshot= capture_screenshot()
        at_home, confidence = self.match_scene(screenshot, self.scene_path['home'], threshold=0.6)
        if not at_home:
            print("Not starting at home.")
            return False
        #1. from home click march button
        clicked = self.clickButton('home','march_button')
        while clicked:
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['march_page'], threshold=0.6)
            if matched:
                break
        #2. from march_page click march image
        clicked = self.clickButton('march_page','march_image')
        while clicked:
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['battlefield_select'], threshold=0.6)
            if matched:
                break
        return True
    
    def use_speed_up_tool(self):
        #TODO rethink whether this is necessary
        pass
    def repair(self, type, ji, injury_level):
        """
        Repair certain type of touken above certain injury_level
        
        Parameters:
        -type: type of token, duandao, taidao...
        -ji: whether it is ji touken
        -injury_level: l,m,s for light, medium, severe

        Cycle:
        1.from home click repair button
        2.from repair page, filter order button
        3.TODO by type, select the type of token
        4.TODO by ji, select the ji button
        5.TODO by injury_level, select the injury_level, at 10/26/2024, I will hard code what to select
        --repeat 7-11 until 6. check for no_repair_need_scene
        7.select the filtered touken (one by one), {'coordinates': [(857, 177)], 'w': 147, 'h': 106}
        8.-from repair_select scene select the start repair button
        9.-from repair scene, select the speed_up button
        10.-from use_speed_up_tool_scene click yes (768,768)
        11.-wait for 4 secend(for repair animation)
         
        """
        screenshot= capture_screenshot()
        matched, confidence = self.match_scene(screenshot, self.scene_path["home"], threshold=0.7)
        if not matched:
            print("Repair task, not at home.")
            return False
        clicked = self.clickButton('home','repair_button')
        while clicked:
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            
            matched, confidence = self.match_scene(screenshot, self.scene_path['repair'], threshold=0.6)
            if matched:
                break
        self.click_x_y(752,285)#first repair slot
        while True:
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['repair_select'], threshold=0.6)
            if matched:
                break
        clicked = self.clickButton("repair_select","filter_order")
        while clicked:
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            
            matched, confidence = self.match_scene(screenshot, self.scene_path['repair_select_option'], threshold=0.6)
            if matched:
                break
        self.click_x_y(807,305)
        time.sleep(1)
        #self.click_x_y(807,837)
        #time.sleep(1)
        self.click_x_y(1100,837)
        time.sleep(1)
        self.click_x_y(1436,837)
        screenshot= capture_screenshot()
        matched, confidence = self.match_scene(screenshot, self.scene_path['no_repair_need'], threshold=0.6)
        while not matched:
            self.click_x_y(921,233)
            time.sleep(1)
            self.click_x_y(1436,837)
            time.sleep(1)
            self.click_x_y(1420,290)
            time.sleep(1)
            self.click_x_y(768,768)
            time.sleep(5)
            self.click_x_y(752,285)#first repair slot
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['no_repair_need'], threshold=0.6)
        print("Repair task, finished repair.")
        #click home button
        self.click_x_y(1816,1033)
        return True


    def equipt(self, team_num = 1):
        """
        Helper method to replace equiptment

        Parameters:
        -team_num: which team to equipt

        Cycle:
        1. start from home, click team button
        2. from team select, from top to bottom, click select, automatic equipt, confirm
        3. return home
        """   
        screenshot= capture_screenshot()
        at_home, confidence = self.match_scene(screenshot, self.scene_path['home'], threshold=0.6)
        if not at_home:
            print("Task put equiptment. Not starting at home.")
            return False
        clicked = self.clickButton("home","team_button")
        at_correct_scene = self.wait_for_scene('team_select',0.7)
        if not at_correct_scene:
            return False
        
        

    def march_udg(self, level):
        """
        The march method for underground activity.
        
        Parameters:
        -level: which level to go

        Cycle:
        1. from home click march button
        2. from march_page click march image
        3. from battlefield_select select underground activity
        4. from underground_scene click select_team(1418,919)
        5. from battle_set_out click march_now
        6. from underground_march_confirm click yes(780,567)
        --repeat 7. click keep_on(1242,659)/find the reverse format until stopping criteria--
            8. if see home and severe_injure_warning1, exit loop
        9. repair all mid injure&severe injure 极短
        """
        self.repair("duandao", True, "m")
        time.sleep(self.speed)
        at_battlefield = self.home_to_battle_select()
        if not at_battlefield:
            print("Didn't ends up at battlefield_select")
            return False
        clicked = self.clickButton("battlefield_select","underground")
        while clicked:
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['underground_scene'], threshold=0.6)
            if matched:
                break
        self.click_x_y(1418,919)
        
        while True:
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['battle_set_out'], threshold=0.6)
            if matched:
                break
        time.sleep(1)
        self.click_x_y(1418,919)#set out now
        time.sleep(1)
        self.click_x_y(780,567)#assuming setting out will not have severe injure touken
        time.sleep(1)
        screenshot= capture_screenshot()
        matched_home, confidence = self.match_scene(screenshot, self.scene_path['home'], threshold=0.6)
        matched_injure, confidence = self.match_scene(screenshot, self.scene_path['severe_injure_warning1'], threshold=0.7)
        while not matched_home and not matched_injure:
            self.click_x_y(1185,733)#(1281,659)手动逆行
            time.sleep(2)
            screenshot= capture_screenshot()
            matched_home, confidence = self.match_scene(screenshot, self.scene_path['home'], threshold=0.6)
            matched_injure, confidence = self.match_scene(screenshot, self.scene_path['severe_injure_warning1'], threshold=0.7)
        if matched_injure:
            self.click_x_y(1185,733)#click no first.
            time.sleep(1)
            at_home = self.go_home()
            if at_home:
                print("Successfully runned once, keep going.")
                return True
        return True
                
    

    def check_state_reconnect(self):
        """
        Helper function to reconnect to task if stuck at unexpected place

        So far it's go home and restart.
        """
        click_home_botton = ["underground_march_confirm","add_teammate","battle_set_out","battlefield_select","char_select","healing_team","march_page","no_repair_need","repair","repair_select","team_select", "underground_select"]
        screenshot= capture_screenshot()
        scene_now, confidence = find_best_match_in_scene(screenshot, self.scene_path, threshold=0.6)
        if scene_now == 'next_step': #TODO, implement a way to reconnect to the current task...
            #self.injury_check_in_battle
            at_home = self.go_home()
            if at_home:
                print("From next_step, Reconnected.")
                return True
        elif scene_now in click_home_botton:
            self.click_x_y(1814,1024)#home button
            print(f"From {scene_now}, Reconnected.")
            return True
        elif scene_now == 'travel_return':
            self.wait_for_scene('home',0.7)
        elif  scene_now == 'team_in_repair':
            clicked = self.clickButton('team_in_repair','repair_button')
            at_repair = self.wait_for_scene('repair')
            if not at_repair:
                print(f'from {scene_now} clicked repair button, not end up in repair.')
                return False
            else:
                num_of_button = self.button_targets['speed_up'].get_num("repair")
                for i in range(num_of_button):
                    #for each repairing touken, speed up
                    clicked = self.clickButton('repair','speed_up', i ,0.8)
                    if clicked:
                        self.click_x_y(768,768)# confirm speed up
                        time.sleep(4) #wait for animation 
                print('Speeded up all repair.')
                return True

        
        else:
            self.wait_for_scene('home',0.7)
            print(f"No preset solution for this scene: {scene_now}")
            return False
    



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
    
        

    def march(self, map_name, stop_before_boss, healing):
        """
        Compare multiple target templates to the current screenshot and return the name of the target with the highest confidence.
        
        Parameters:
        - screenshot: The current screenshot (OpenCV image).
        - target: path to the target_template.
        - threshold: Matching threshold (0-1). A higher value means a more exact match is required.
        
        Returns:
        - again: boolean of whether to keep marching the same map
        
        """
        at_battlefield = self.home_to_battle_select()
        if not at_battlefield:
            print("Didn't ends up at battlefield")
            return False
        #3. TODO select era click era
        #4. TODO select location click location
        
        #so far default select l3, so far I will assume
        #the l3 click position is the safe default click(only when in battle)
        clicked = self.click3()
        while clicked:
            time.sleep(self.sleep)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path['battle_set_out'], threshold=0.8)
            if matched:
                break
        #5. from battle_set_out click march_now
        clicked = self.clickButton('battle_set_out','march_now')
        while clicked:
            time.sleep(self.speed)
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
                        time.sleep(self.speed)
                        screenshot= capture_screenshot()
                        
                        matched, confidence = self.match_scene(screenshot, self.scene_path['battle_set_out'], threshold=0.7)
                        if matched:
                            break
                    clicked = self.clickButton('battle_set_out','home_button')
                    while clicked:
                        time.sleep(self.speed)
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
            time.sleep(self.speed)
            screenshot= capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path["next_step"], threshold=0.7)
            if matched:
                #6-1. if stop, click return_base
                #screenshot= capture_screenshot()
                if stop_before_boss:
                    found_stop, _ =check_end_pt(screenshot, self.map_targets[map_name],threshold=0.78)
                    if found_stop:
                        at_home = self.go_home()
                        if at_home:
                            print("Successfully runned once, keep going.")
                            return True
                    #not at stop yet
                    clicked = self.clickButton('next_step','keep_on')
                    injury = self.injury_check_in_battle()
                    if injury:
                        print('Someone severely injured, stop.')
                        return False
                else:
                    #no need to stop before boss
                    clicked = self.clickButton('next_step','keep_on')
                    #8. check severe_injure warning 1&2
                    injury = self.injury_check_in_battle()
                    if injury:
                        print('Someone severely injured, stop.')
                        return False
            
        
