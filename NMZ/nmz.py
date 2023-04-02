import time
import random
import datetime

import utilities.api.item_ids as ids
import utilities.color as clr
from model.bot import BotStatus
from model.osrs.osrs_bot import OSRSBot
from utilities.api.status_socket import StatusSocket
from utilities.geometry import Point, RuneLiteObject
from utilities.api.morg_http_client import MorgHTTPSocket


class OSRSNMZ(OSRSBot):
    def __init__(self):
        title = "Nightmare Zone"
        description = "Items: Overloads, Absorptions, Dwarven rock cake. Must use methods currently in PR for getting boost level. https://github.com/kelltom/OSRS-Bot-COLOR/pull/152 ."
        super().__init__(bot_title=title, description=description)
        self.running_time = 2

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 720)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Bot will run for {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):  # sourcery skip: low-code-quality, use-named-expression
        # API setup
        api = StatusSocket()
        api_m = MorgHTTPSocket()

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()
        
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        # Initialize absorb timer
        absorb_timer = time.time()
        
        absorb_interval = random.randint(1, 5)

        while time.time() - start_time < end_time:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            # Absorb every 60 seconds
            if time.time() - absorb_timer > absorb_interval:
                #print(f"{current_time} Waited {absorb_interval}s before clicking an absorb")
                self.__absorb(api)
                absorb_timer = time.time()
                absorb_interval = random.randint(60, 125)

            if hp := api_m.get_hitpoints():
                if hp[0] > 1 and api.get_is_boosted("ATTACK") == True:
                    #print(f"{current_time} More than 1hp, trying to drain")
                    self.__drock(api)
                elif hp[0] >= 51 and api.get_is_boosted("ATTACK") == False:
                    #print(f"{current_time} 51 or more hp, Not boosted, trying to boost")
                    self.__ovload(api)

            # Update progress
            self.update_progress((time.time() - start_time) / end_time)
                    
    def __absorb(self, api: StatusSocket):
        #self.log_msg("Absorption is low.")
        abbys = [ids.ABSORPTION_4, ids.ABSORPTION_3, ids.ABSORPTION_2, ids.ABSORPTION_1]
        slots = api.get_inv_item_indices(abbys)
        if len(abbys) == 0:
            self.log_msg("No Absorption pots found...")
            return
        self.log_msg("Chuggin Absorption...")
        self.mouse.move_to(self.win.inventory_slots[slots[0]].random_point(), mousespeed="fastest")
        self.mouse.click()
        time.sleep(0.5)
        
    def __ovload(self, api: StatusSocket):
        loadies = [ids.OVERLOAD_1, ids.OVERLOAD_3, ids.OVERLOAD_2, ids.OVERLOAD_1]
        slots = api.get_inv_item_indices(loadies)
        if len(loadies) == 0:
            self.log_msg("No ovloads found...")
            return
        self.log_msg("Sippin loads......")
        self.mouse.move_to(self.win.inventory_slots[slots[0]].random_point(), mousespeed="fastest")
        self.mouse.click()
        time.sleep(9)
        
    def __drock(self, api: StatusSocket):
        rock = [ids.DWARVEN_ROCK_CAKE, ids.DWARVEN_ROCK_CAKE_7510]
        slots = api.get_inv_item_indices(rock)
        if len(rock) == 0:
            self.log_msg("No dwarven rock cake found...")
            return
        self.log_msg("Chewin rock...")
        self.mouse.move_to(self.win.inventory_slots[slots[0]].random_point(), mousespeed="fastest")
        self.mouse.click()
        time.sleep(0.5)
        
    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()