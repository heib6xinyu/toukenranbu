from utility import *
import logging
class SceneTimeoutError(Exception):
    def __init__(self, state, march_name, message="Scene load timeout"):
        self.state = state
        self.march_name = march_name
        self.message = message
        super().__init__(f"{message} in state {self.state} in march {self.march_name}")

class ButtonNotFoundError(Exception):
    def __init__(self, state, march_name, message="Button Not Found"):
        self.state = state
        self.march_name = march_name
        self.message = message
        super().__init__(f"{message} in state {self.state} in march {self.march_name}")

class CharNotFoundError(Exception):
    def __init__(self, state, march_name, message="Character Not Found"):
        self.state = state
        self.march_name = march_name
        self.message = message
        super().__init__(f"{message} in state {self.state} in march {self.march_name}")
                      
class March:
    def __init__(self, team, scene_path, battlefield_path, button_path, status_path, touken_path,button_targets, map_targets, touken_targets, timeout = 30, speed = 3):
        self.team = team
        self.scene_path = scene_path  # Dictionary of path to scenes
        self.battlefield_path = battlefield_path  # Dictionary of path to battlefields
        self.button_path = button_path  # Dictionary of path to buttons
        self.status_path = status_path  # Dictionary of path to status
        self.touken_path = touken_path
        self.button_targets = button_targets #dimension info for buttons
        self.map_targets = map_targets #dimension info for maps
        self.touken_targets = touken_targets
        self.march_name = None
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
        adb_tap(912,89)
        return True
    def click_x_y(self,x,y):
        adb_tap(x,y)
        return True
    def swipe_to_right_l(self):
        adb_swipe(349, 562, 1345, 562, 50)
        return True
    def swipe_to_left_l(self):
        adb_swipe(1345, 562, 349, 562, 50)
        return True
    def swipe_to_right_s(self):
        adb_swipe(349, 562, 995, 562, 50)
        return True
    def swipe_to_left_s(self):
        adb_swipe(995, 562, 349, 562, 50)
        return True
    def swipe_to_right_m(self):
        adb_swipe(618, 562, 1251, 562, 50)
        return True
    def swipe_to_left_m(self):
        adb_swipe(1251, 562, 618, 562, 50)
        return True



        
    def clickButton(self, start_scene, button, end_scene, num = 0, threshold=0.5):
        coords = self.button_targets[button].get_coordinates(start_scene)
        x,y = coords['coordinates'][num]
        
        w = coords['w']
        h = coords['h']
        middle_x = w // 2
        middle_y = h // 2
        
        adb_tap(x+middle_x, y+middle_y)
        self.wait_for_scene(end_scene,threshold) 
        
        

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
                return True #or just break?
            elapsed_time = time.time() - start_time
            if elapsed_time > self.timeout:
                raise SceneTimeoutError(self.state, self.march_name, f"{scene} time out")
                
            


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
        clicked = self.clickButton('next_step','return_base','go_home')           
        #6-2. click yes
        clicked = self.clickButton('go_home','yes','home')
        return True
    
    def home_to_battle_select(self):
        self.wait_for_scene('home')#TODO figure out at which level should i just throw exception and where to try except
        #1. from home click march button
        clicked = self.clickButton('home','march_button','march_page')
        #2. from march_page click march image
        clicked = self.clickButton('march_page','march_image','battlefield_select')
        return True
    
    def use_speed_up_tool(self):
        #TODO rethink whether this is necessary
        pass
    
    def search_char(self, path, threshold=0.6):
        """
        Helper function to get the desire target defined by path from char_select scene
        return the index of confirm button's coordinates
        """
        self.state = f"Search_char {path}"
        
        top_left = None
        # TODO if other button needed, change this hard code part
        coordinates = self.button_targets['confirm'].get_coordinates('char_select')['coordinates']
        start_time = time.time()
        while top_left is None:
            screenshot_image = capture_screenshot()
            # Display the screenshot (optional)
            top_left, width, height, num_injure = find_template_in_screenshot(screenshot_image, path, threshold)
            if top_left:
                (_,top_left_y)  = top_left
                closest_index = min(range(len(coordinates)), key=lambda i: abs(coordinates[i][1] - top_left_y))
                return closest_index
            self.swipe_to_left_l()
            time.sleep(3)
            # at_end = check_area(screenshot_image, self.button_targets['swipe_right_grey'], 'char_select', threshold=0.6)
            # if at_end:
            #     raise CharNotFoundError(self.state, self.march_name, f"Reach end, {path} not found")
            if time.time()-start_time > 30:#check for end is too difficult, use time out instead
                print(f"Timeout, {path} not found.")
                return None

    def search_injured_char(self, threshold=0.6):
        """
        Helper function to get the desire target defined by path from char_select scene
        return the index of confirm button's coordinates
        """
        self.state = f"search_injured_char"
        
        found = False
        start_time = time.time()
        while not found:
            screenshot_image = capture_screenshot()
            # Display the screenshot (optional)
            found, num = check_area(screenshot_image, self.button_targets['severe_injure'],'char_select', threshold=threshold)
            if found:
                return num
            self.swipe_to_left_l()
            time.sleep(3)
            # at_end = check_area(screenshot_image, self.button_targets['swipe_right_grey'], 'char_select', threshold=0.6)
            # if at_end:
            #     raise CharNotFoundError(self.state, self.march_name, f"Reach end, {path} not found")
            if time.time()-start_time > 30:#check for end is too difficult, use time out instead
                print(f"Timeout, severe_injure not found.")
                return None    


    def filter_touken(self, touken_type, ji):
        """
        Helper function to filter for desire touken's type
        
        Parameter:
        -touken_type:
        -ji: what to filter

        """ 
        self.state = "Filter_touken"
        self.wait_for_scene('char_select')
        screenshot= capture_screenshot()
        filter,_ = check_area(screenshot,self.button_targets['filter_order'], 'char_select', threshold=0.5)
        filtering,_ = check_area(screenshot,self.button_targets['filtering'], 'char_select', threshold=0.5)
        
        if filter:
            #haven't put in any filter
            self.clickButton('char_select', 'filter_order','filter_all', threshold=0.5)
        elif filtering:
            self.clickButton('char_select', 'filtering','filter_all', threshold=0.5)
        match touken_type:
            case 'duandao':
                self.click_x_y(781,316)
            case 'jian':
                self.click_x_y(1096,525)
            case 'taidao':
                self.click_x_y(792,422)
            case _:
                print(f'No matched type {touken_type}.')
        if ji:
            self.click_x_y(792,734)
        else:
            self.click_x_y(484,372)
        self.clickButton('filter_all', 'filter_confirm', 'char_select')



    def healing_march(self):
        self.clickButton('healing_team','march_button','march_page')
        self.clickButton('march_page','march_image','battlefield_select')
        self.click1()
        self.wait_for_scene('battle_set_out')
        self.clickButton('battle_set_out','march_now','severe_injure_warning1')
        #so far hard code the confirm set out because scene matching is time consuming
        self.click_x_y(792,710)
        time.sleep(self.speed)
        self.click_x_y(792,710)
        self.wait_for_scene("1-1")
        #assume in battlefield
        screenshot = capture_screenshot()
        matched, confidence = self.match_scene(screenshot, self.scene_path["home"], threshold=0.7)  
        while not matched:
            time.sleep(self.speed)
            self.click_x_y(1199,728)#continue marching
            screenshot = capture_screenshot()
            matched, confidence = self.match_scene(screenshot, self.scene_path["home"], threshold=0.7)  
        return True


        

    def healing(self, touken_type, touken_ji):
        """
        Function to use baishan to heal severe injured touken type

        Paramater: 
        -touken_type:
        -touken_ji: status to filter the touken_with

        """
        self.state = f'healing {touken_type}, {touken_ji}'
        
        self.clickButton('team_select','ungroup','confirm_ungroup')
        self.clickButton('confirm_ungroup','yes','team_select',threshold=0.6)
            
        screenshot = capture_screenshot()
        found,_ = check_area(screenshot,self.button_targets['baishan'], 'healing_team', threshold=0.5)
        
        if not found: #no baishanjiguang in team
            self.clickButton('healing_team','select','equipt_manage')
            self.clickButton('equipt_manage','replace','char_select')
            #self.filter_touken(self.touken_targets['baishanjiguang'])#pass baishanjiguang target
            #TODO: when the selected target has very few number, the char_select may not be able to recognize it.
            confirm_num = self.search_char(self.touken_path['baishanjiguang'])
            self.clickButton('char_select','confirm','healing_team',confirm_num)
        self.clickButton('healing_team','add_char','char_select', 1)

        self.filter_touken(touken_type,touken_ji)#pass touken's target
        
        confirm_num = self.search_injured_char(0.6)
        if confirm_num is None:
            # will be in char_select
            print('No injured touken.')
            self.click_x_y(1836,1022)#本丸
            self.wait_for_scene('home')
            return False
        self.clickButton('char_select','confirm','healing_team',confirm_num)
        self.clickButton('healing_team','select','equipt_manage',1)
        self.clickButton('equipt_manage', 'auto_equipt_valid','finished_auto_equipt')#TODO: if no equiptment, build equuipment
        self.click_x_y(974,713)#yes
        self.wait_for_scene('equipt_manage')
        self.healing_march()
        return True

    def select_predefine_team(self,team_num = 0):
        self.wait_for_scene('team_select', 0.6)
        self.clickButton('team_select','record_team','pre_select_team')
        for _ in range(team_num):
            self.swipe_to_left_m()
        self.click_x_y(768,972)#编入部队
        self.wait_for_scene('confirm_team')
        self.click_x_y(752,988)#是
        self.wait_for_scene('team_select')
        return True

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
            raise SceneTimeoutError(self.state, self.march_name, "Repair task, not at home.")
        clicked = self.clickButton('home','repair_button','repair')
        self.click_x_y(752,285)#first repair slot
        #self.wait_for_scene('repair_select')#TODO should account for loading time.
        clicked = self.clickButton("repair_select","filter_order",'repair_select_option')
        self.click_x_y(807,305)
        time.sleep(1)
        #self.click_x_y(807,837)
        #time.sleep(1)
        self.click_x_y(1100,837)
        time.sleep(1)
        self.click_x_y(1436,837)
        screenshot= capture_screenshot()
        matched, confidence = self.match_scene(screenshot, self.scene_path['no_repair_need'], threshold=0.6)
        start_time = time.time()
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
            elapsed_time = time.time() - start_time
            if elapsed_time>self.timeout:
                raise SceneTimeoutError(self.state, self.march_name, "Repair timeout.")
        print("Repair task, finished repair.")
        #click home button
        self.click_x_y(1816,1033)
        return True


    def equipt(self, team_num = 1,threshold = 0.7):
        """
        Helper method to replace equiptment

        Parameters:
        -team_num: which team to equipt

        Cycle:
        1. start from home, click team button
        2. from team select, from top to bottom, click select, automatic equipt, confirm
        3. return home
        """   
        self.wait_for_scene("team_select",threshold)
        for i in range(6):
            self.clickButton('team_select','select','equipt_manage',i,threshold)
            self.clickButton('equipt_manage', 'auto_equipt_valid','finished_auto_equipt', threshold=threshold)#TODO: if no equiptment, build equuipment
            self.click_x_y(974,713)#yes
            self.wait_for_scene('equipt_manage',threshold)
            self.click_x_y(915,138)#return
            self.wait_for_scene('team_select',threshold)

        return True
        
        

    def march_udg(self, level=99, start = 99, team = 0):
        """
        The march method for underground activity.
        
        Parameters:
        -level: which level to go
        -level: start level (your highest level now)
        -team: which preset team to select
            so far, team 0 is 极太一队
                    team 1 is 极短二队#TODO come up with a way to modify this

        Cycle:
        1. from home click march button
        2. from march_page click march image
        3. from battlefield_select select underground activity
        4. from underground_scene click select_team(1418,919)
        5. from battle_set_out click march_now
        6. from underground_march_confirm click yes(780,567)
        --repeat 7. click keep_on(1242,659)/find the reverse format until stopping criteria--
            8. if see home and severe_injure_warning1, exit loop
        9. repair all mid injure&severe injure 极短 /or baishan heal
        """
        def go_to_level(level, start=99):
            """
            Helper method to go to desired level from start level
            Assume start at level 99 and go back if not specific instruction
            """
            modnum = start%level
            gewei = modnum%10
            shiwei = int(modnum/10)
            for _ in range(gewei):
                #个位数降i
                self.click_x_y(1000,770)#down arrow
                time.sleep(1)
            for _ in range(shiwei):
                self.click_x_y(850,770)#down arrow
                time.sleep(1)
        if team ==0:
            #极太队，白山治疗
            try:
                self.wait_for_scene('home')
                self.clickButton('home','team_button','team_select')
                screenshot= capture_screenshot()
                path = self.status_path['severe_injure']
                top_left, width, height,num_injure = find_template_in_screenshot(screenshot, path, threshold=0.60)
                if top_left:
                    #there is severe injury, heal all of them
                    for i in range((max(num_injure,6))):
                        
                        more_injure = self.healing('taidao',True)
                        if not more_injure: #should be at home
                            break
                        self.clickButton('home','team_button','healing_team')


                else:
                    #no one injured.
                    #click home
                    self.click_x_y(1804,1038)
                    self.wait_for_scene('home')
                #after healing, most likely will be at home
                self.clickButton('home','team_button','team_select',threshold=0.5)
                self.select_predefine_team()
                #click home
                self.click_x_y(1804,1038)
            except Exception  as e:
                logging.error(str(e))
                print("Error:", e)
                print('Baishan Heal task failed.')
                return False   
        elif team ==1:
            #极短队，直接治疗
            try:
                repair_success = self.repair("duandao", True, "m")
            except Exception  as e:
                logging.error(str(e))
                print("Error:", e)
                print('Repair task failed.')
                return False
        try:
            time.sleep(self.speed)
            at_battlefield = self.home_to_battle_select()
            clicked = self.clickButton("battlefield_select","underground",'underground_scene')
        except Exception as e:
            logging.error(str(e))
            print("Error:", e)
            print('Go to underground task failed.')
            return False
            
        #go to level
        go_to_level(level, start)

        try:
            self.click_x_y(1418,919)
            at_scene = self.wait_for_scene('battle_set_out',0.6)
            self.click_x_y(1418,919)#set out now
            
            at_scene = self.wait_for_scene('underground_march_confirm')
            self.click_x_y(780,567)#if not severe injured, click yes and set out.
            screenshot= capture_screenshot()
            matched_home, confidence = self.match_scene(screenshot, self.scene_path['home'], threshold=0.6)
            matched_injure, confidence = self.match_scene(screenshot, self.scene_path['severe_injure_warning1'], threshold=0.7)
            while not matched_home and not matched_injure:
                self.click_x_y(1281,659)#(1281,659)手动逆行(1185,733)普通
                time.sleep(1)
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
        except Exception as e:
            logging.error(str(e))
            print("Error:", e)
            print('Loop underground task failed.')
            return False
                
    

    def check_state_reconnect(self):
        """
        Helper function to reconnect to task if stuck at unexpected place

        So far it's go home and restart.
        """
        click_home_botton = ["underground_march_confirm","add_teammate","battle_set_out","battlefield_select","char_select","healing_team","march_page","no_repair_need","repair","repair_select","team_select", "underground_scene","underground_select"]
        screenshot= capture_screenshot()
        scene_now, confidence = find_best_match_in_scene(screenshot, self.scene_path, threshold=0.6)
        if scene_now == 'next_step': #TODO, implement a way to reconnect to the current task...
            #self.injury_check_in_battle
            at_home = self.go_home()
            if at_home:
                print(f"From {scene_now}, Reconnected.")
                return True
            else:
                print(f"From {scene_now}, Reconnected Failed.")
                return False
        elif scene_now in click_home_botton:
            self.click_x_y(1814,1024)#home button
            print(f"From {scene_now}, Reconnected.")
            return True
        elif scene_now == 'travel_return':
            at_scene = self.wait_for_scene('home',0.7)
            if at_scene:
                print(f"From {scene_now}, Reconnected.")
                return True
        elif scene_now == 'team_in_repair':
            clicked = self.clickButton('team_in_repair','repair_button','repair')
            at_repair = self.wait_for_scene('repair')
            if at_repair:
                num_of_button = self.button_targets['speed_up'].get_num("repair")
                for i in range(num_of_button):
                    #for each repairing touken, speed up
                    clicked = self.clickButton('repair','speed_up','repair', i ,0.8)
                    
                    time.sleep(4) #wait for animation 
                print('Speeded up all repair.')
                return True
        elif scene_now == 'repair':
            num_of_button = self.button_targets['speed_up'].get_num("repair")
            for i in range(num_of_button):
                #for each repairing touken, speed up
                clicked = self.clickButton('repair','speed_up','repair', i ,0.8)
                
                time.sleep(4) #wait for animation 
            print('Speeded up all repair.')
            return True
        elif scene_now == 'need_equipt':
            self.click_x_y(761,706)#整备刀装
            self.equipt()
            print('Need equpit, reconnect.')
        elif scene_now == 'severe_injure_warning1':
            self.click_x_y(1130,717)#否
            self.wait_for_scene('battle_set_out')
            self.click_x_y(1818,1027)#本丸
            self.wait_for_scene('home')
            print('Severe injure warning from battle set out, reconnect.')

        else:
            at_scene = self.wait_for_scene('home',0.7)

    



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
            
        
