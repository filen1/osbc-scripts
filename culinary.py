import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject
import random
import pyautogui as pag

'''
Includes functions and code from: https://github.com/WillowsDad
Place file in OSRS-Bot-COLOR/src/model/osrs
In OSRS-Bot-COLOR/src/model/osrs/__init__.py add: from .culinary import OSRSCulinary
In NPC Indicators plugin make the color PINK and the border 7
In Object Markers plugin make the color CYAN and the border 7
In OSRS-Bot-COLOR/src/utilities/api/item_ids.py add 

burnt_food = [
    BURNT_FISH,
    BURNT_FISH_343,
    BURNT_FISH_357,
    BURNT_FISH_367,
    BURNT_FISH_369,
    BURNT_SWORDFISH,
    BURNT_LOBSTER,
    BURNT_SHARK,
    BURNT_MANTA_RAY,
    BURNT_SEA_TURTLE,
    BURNT_PITTA_BREAD,
    BURNT_CAKE,
    BURNT_STEW,
    BURNT_CURRY,
    BURNT_CHICKEN,
    BURNT_MEAT,
    BURNT_BATTA,
    BURNT_PIZZA,
    BURNT_BREAD,
    BURNT_PIE,
    BURNT_KARAMBWAN,
    BURNT_POTATO,
    BURNT_RABBIT,
    BURNT_MONKFISH,
    BURNT_SHRIMP,
    BURNT_DARK_CRAB,
    BURNT_ANGLERFISH,
    BURNT_FISH_20854,
    BURNT_FISH_23873,
    TROUT,
    SALMON,
]

Known issues: Has to click twice to begin cooking. Requires 26 raw_fish or 26 burnt_food to operate.
'''

class OSRSCulinary(OSRSBot):
    def __init__(self):
        bot_title = "Culinary"
        description = "This bot will catch fish and cook them at the barbarion village. Position your character with both the tagged fire and fishing spots in view."
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 1
        self.take_breaks = False

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])
        self.options_builder.add_slider_option("delay_min", "How long to take between actions (min) (MiliSeconds)?", 300,3000)
        self.options_builder.add_slider_option("delay_max", "How long to take between actions (max) (MiliSeconds)?", 850,3000)
        
    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            elif option == "delay_min":
                self.delay_min = options[option]/1000
            elif option == "delay_max":
                self.delay_max = options[option]/1000
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def random_sleep_length(self, delay_min=0, delay_max=0):
        """Returns a random float between min and max"""
        if delay_min == 0:
            delay_min = self.delay_min
        if delay_max == 0:
            delay_max = self.delay_max
        return rd.fancy_normal_sample(delay_min, delay_max)

    def main_loop(self):
        self.setup()

        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())

        self.mouse.click()

        self.cfish = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        self.roll_chance_passed = False

        while time.time() - start_time < end_time:
            # 15% chance to take a break
            if rd.random_chance(probability=0.15) and self.take_breaks:
                self.take_break(max_seconds=30, fancy=True)

            while not self.api_s.get_is_inv_full():
                self.log_msg("Inventory is not full...")

                if len(self.api_s.get_inv_item_indices(ids.raw_fish)) < 26:
                    self.log_msg("Inventory is not full. Less than 26 raw_fish...")
                    if self.api_m.get_is_player_idle():
                        self.log_msg("Player is idle with an unfilled inventory and less than 26 raw_fish, calling find_spot...")
                        self.find_spot()
                time.sleep(self.random_sleep_length())

            if self.api_s.get_is_inv_full():
                if len(self.api_s.get_inv_item_indices(ids.raw_fish)) >= 1:
                    self.log_msg("Inventory is full with one or more raw_fish...")
                    if self.api_m.get_is_player_idle():
                        self.log_msg("Player is idle with a full inventory and one or more raw fish, calling find_fire...")
                        self.find_fire()
                    #time.sleep(self.random_sleep_length())
                elif len(self.api_s.get_inv_item_indices(ids.burnt_food)) >= 26:
                    self.log_msg("Inventory is full with 26 of more burnt_food items, calling __drop_fish...")
                    self.__drop_fish()
                time.sleep(self.random_sleep_length())

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def setup(self):
        """
        Sets up loop variables, checks for required items, and checks location.
            Args:
                None
            Returns:
                None
        """

        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()

    def choose_fire(self):
        """
        Grabs all CYAN(0,255,255) rectangles and sorts them into a list.
            Returns: Closest fire from list of rectangles or none if no spots are found
            Args: None
        """

        if fires := self.get_all_tagged_in_rect(self.win.game_view, clr.CYAN):
            fires = sorted(fires, key=RuneLiteObject.distance_from_rect_center)

            if len(fires) >= 1:
                return fires[0]

        else:
            self.log_msg("No fires found...")
            return (self.choose_fire())

    def find_fire(self):
        """
        This will use choose_fire to find a fire and click it.
        Returns: 
            void
        Args: 
        """

        self.log_msg("Finding Fire...")
        fire = self.choose_fire()

        self.log_msg("Moving mouse to the fire...")
        self.mouse.move_to(fire.random_point())

        time.sleep(self.random_sleep_length())

        
        self.log_msg("Clicking on the fire...")
        self.mouse.click()

        time.sleep(self.random_sleep_length())


        while self.api_m.get_is_player_idle():
            self.log_msg("Player is idle...")
            pag.press('space')

            self.log_msg("Begin Cooking...")

        time.sleep(self.random_sleep_length())
        return

    def choose_spot(self):
        """
        Grabs all PINK(255,0,231) rectangles and sorts them into a list.
            Returns: Closest fishing spot from list of rectangles or none if no spots are found
            Args: None
        """

        if spots := self.get_all_tagged_in_rect(self.win.game_view, clr.PINK):
            spots = sorted(spots, key=RuneLiteObject.distance_from_rect_center)

            if len(spots) >= 1:
                return spots[0]

        else:
            self.log_msg("No fishing spots found...")
            return (self.choose_spot())

    def find_spot(self):
        """
        This will use choose_spot to find a fishing spot and click it.
        Returns: 
            void
        Args: 
        """

        self.log_msg("Searching for fishing spot...")
        spot = self.choose_spot()

        self.log_msg("Moving mouse to fishing spot...")
        self.mouse.move_to(spot.random_point())

        time.sleep(self.random_sleep_length())

        self.log_msg("Clicking on the fishing spot...")
        self.mouse.click()

        time.sleep(self.random_sleep_length())

        return

    def __drop_fish(self):
        """
        Private function for dropping raw fish. This code is used in multiple places, so it's been abstracted.
        Since we made the `api` and `fish` variables assigned to `self`, we can access them from this function.
        """
        slots = self.api_s.get_inv_item_indices(ids.burnt_food)
        self.drop(slots)
        self.cfish += len(slots)
        self.log_msg(f"Fish cooked/burnt: ~{self.cfish}")
        time.sleep(1)