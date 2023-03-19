import time
import random

import pyautogui as pg
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject


class OSRSBVFC(OSRSBot):
    def __init__(self):
        bot_title = "Barbarian Village Fish + Cook"
        description = "Credits to https://github.com/WillowsDad for take_breaks code, etc. This bot is for fishing and cooking at barbarian village. Fishing spots CYAN, fire PINK."
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1
        self.take_breaks = False
        self.delay_min = 265/1000
        self.delay_max = 580/1000

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])
        self.options_builder.add_slider_option("delay_min", "How long to take between actions (min) (MiliSeconds)?", 300,3000)
        self.options_builder.add_slider_option("delay_max", "How long to take between actions (max) (MiliSeconds)?", 650,3000)

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] !=[]
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
        self.log_msg(f"Bot will wait between {self.delay_min} and {self.delay_max} seconds between actions.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. To see what the APIs can offer you, see here: https://github.com/kelltom/OSRS-Bot-COLOR/tree/main/src/utilities/api.
          For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.` operator to access their
          functions.
        """
        # Setup APIs
        self.setup()

        # Main loop
        while time.time() - self.start_time < self.end_time:

            runtime = int(time.time() - self.start_time)
            minutes_since_last_break = int((time.time() - self.last_break) / 60)
            seconds = int(time.time() - self.last_break) % 60
            percentage = (self.multiplier * .02)  # this is the percentage chance of a break
            self.roll_chance_passed = False

            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.
            self.raw = len(self.api_m.get_inv_item_indices(ids.raw_fish))
            self.is_idle = self.api_m.get_is_player_idle()
            self.burnt = len(self.api_m.get_inv_item_indices(ids.burnt_food))
            self.inv_full = self.api_m.get_is_inv_full()
            
            if self.burnt == 0 and not self.inv_full:
                if self.is_idle:
                    time.sleep(1)
                    self.log_msg("Player is idle with 0 burnt food in inventory...")
                    self.locate_fish()
                    time.sleep(self.random_sleep_length())
            elif self.inv_full and self.raw > 0:
                if self.is_idle:
                    self.log_msg("Player is idle with a full inventory...")
                    self.locate_fire()
                    time.sleep(1)
                    if self.is_idle:
                        self.log_msg("Player is idle since clicking on fire...")
                        time.sleep(self.random_sleep_length())
                        pg.press("space")
            else:
                self.log_msg("Player does not have 0 burnt/cooked fish and unfilled inventory...")
                self.log_msg("Player does as not have 1+ raw fish and a full inventory") 
                self.__drop_fish()  
            time.sleep(1)
                

             # -- End bot actions --
            self.check_break(runtime, percentage, minutes_since_last_break, seconds)
            current_progress = round((time.time() - self.start_time) / self.end_time, 2)
            if current_progress != round(self.last_progress, 2):
                self.update_progress((time.time() - self.start_time) / self.end_time)
                self.last_progress = round(self.progress, 2)
            
    def locate_fish(self):
        """
        This function will locate the fishing spot and click.
        """
        if fish := self.get_all_tagged_in_rect(self.win.game_view, clr.CYAN):
            fish = sorted(fish, key=RuneLiteObject.distance_from_rect_center)
            if len(fish) > 0:
                self.log_msg("Found fishing spot...")
                self.mouse.move_to(fish[0].random_point())
                time.sleep(self.random_sleep_length())
                if self.mouseover_text(contains="Lure", color=clr.OFF_WHITE):
                    self.log_msg("Found fishing spot confirmation...")
                    self.mouse.click()                
                    time.sleep(self.random_sleep_length())
                    
    def locate_fire(self):
        """
        This function will locate the fishing spot and click.
        """
        if fire := self.get_all_tagged_in_rect(self.win.game_view, clr.PINK):
            fire = sorted(fire, key=RuneLiteObject.distance_from_rect_center)
            if len(fire) > 0:
                self.log_msg("Found fire...")
                self.mouse.move_to(fire[0].random_point())
                time.sleep(self.random_sleep_length())
                if self.mouseover_text(contains="Cook", color=clr.OFF_WHITE):
                    self.log_msg("Found fire confirmation...")
                    self.mouse.click()                
                    time.sleep(self.random_sleep_length())
    
    def random_sleep_length(self, delay_min=0, delay_max=0):
        """Returns a random float between min and max"""
        if delay_min == 0:
            delay_min = self.delay_min
        if delay_max == 0:
            delay_max = self.delay_max
        return rd.fancy_normal_sample(delay_min, delay_max)
    
    def setup(self):
        """Sets up loop variables, checks for required items, and checks location.
            This will ideally stop the bot from running if it's not setup correctly.
            * To-do: Add functions to check for required items, bank setup and locaiton.
            Args:
                None
            Returns:
                None"""
        self.end_time = self.running_time * 60
        self.roll_chance_passed = False
        self.last_progress = 0
        self.breaks_skipped = 0
        self.start_time = time.time()
        self.last_break = time.time()
        self.multiplier = 1
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.last_runtime = 0
        self.done = 0
    
    def take_menu_break(self):  # sourcery skip: extract-duplicate-method
        """
        This will take a random menu break [Skills, Combat].]
        Returns: void
        Args: None
        """
        # random amount of seconds to teak a break
        break_time = random.uniform(7, 110)

        if rd.random_chance(.9):
            self.log_msg("Taking a Sklls Tab break...")
            time.sleep(self.random_sleep_length())
            self.mouse.move_to(self.win.cp_tabs[1].random_point())
            if self.mouseover_text(contains="Skills"):
                self.mouse.click()
                self.mouse.move_to(self.win.control_panel.random_point())
                time.sleep(break_time)

                # go back to inventory
                self.mouse.move_to(self.win.cp_tabs[3].random_point())
                time.sleep(self.random_sleep_length())
                if self.mouseover_text(contains="Inventory"):
                    self.mouse.click()
            else:
                self.log_msg("Skills tab not found, break function didn't work...")
                self.stop()
        else:
            self.log_msg("Taking an Equipment menu break...")
            self.mouse.move_to(self.win.cp_tabs[4].random_point())
            time.sleep(self.random_sleep_length())
            if self.mouseover_text(contains="Worn"):
                self.mouse.click()

                self.mouse.move_to(self.win.control_panel.random_point())
                time.sleep(break_time)

                # go back to inventory
                self.mouse.move_to(self.win.cp_tabs[3].random_point())
                if self.mouseover_text(contains="Inventory"):
                    self.mouse.click()

            else:
                self.log_msg("Combat tab not found, break function didn't work...")
                self.stop()
        return
    
    def take_random_break(self, minutes_since_last_break):
        """This will randomly choose a break type and take it. The shorter time since last break, the more likely it is to be a menu break.
        Returns: void
        Args: minutes_since_last_break (int) - the number of minutes passed since the last break."""
        # break type is a random choice from list
        break_type = random.choice(["menu", "break"])

        if break_type == "menu":
            self.log_msg("Taking a menu break...")
            self.take_menu_break()

        if break_type == "break":
            self.log_msg("Taking a break...")

            # check if player is idle
            while not self.api_m.get_is_player_idle():
                self.log_msg("Player is not idle, waiting for player to be idle before taking break...")
                time.sleep(self.random_sleep_length(3,8))

            if minutes_since_last_break > 15:
                self.take_break(15, 120)
            else:
                self.take_break()
    
    def check_break(self, runtime, percentage, minutes_since_last_break, seconds):
        """
        This will roll the chance of a break.
        Returns: void
        Args:
            runtime: int
            percentage: float
            minutes_since_last_break: int
            seconds: int
            self.roll_chance_passed: boolean"""
        if runtime % 15 == 0 and runtime != self.last_runtime:
            if runtime % 60 == 0 or self.roll_chance_passed:   # every minute log the chance of a break
                self.log_msg(f"Chance of random break is {round(percentage * 100)}%")

            self.roll_break(
                percentage, minutes_since_last_break, seconds
            )

        elif self.roll_chance_passed:
            self.log_msg(f"Chance of random break is {round(percentage * 100)}%")

            self.roll_break(
                percentage, minutes_since_last_break, seconds
            )
        self.last_runtime = runtime

    
    def roll_break(self, percentage, minutes_since_last_break, seconds):
        if (
            rd.random_chance(probability=percentage / 4)   # when afk theres weird timing issues so we divide by 4 if not afk
            and self.take_breaks
        ):
            self.reset_timer(
                minutes_since_last_break, seconds, percentage
            )
        self.multiplier += .25  # increase multiplier for chance of random break, we want + 1% every minute 
        self.roll_chance_passed = False
    
    def reset_timer(self, minutes_since_last_break, seconds, percentage):
        self.log_msg(f"Break time, last break was {minutes_since_last_break} minutes and {seconds} seconds ago. \n Chance of random break was {round(percentage * 100)}%")

        self.last_break = time.time()   # reset last break time
        self.multiplier = 1    # reset multiplier

        self.take_random_break(minutes_since_last_break)
        
    def __drop_fish(self):
        """
        Private function for dropping logs. This code is used in multiple places, so it's been abstracted.
        Since we made the `api` and `logs` variables assigned to `self`, we can access them from this function.
        """
        slots = self.api_s.get_inv_item_indices(ids.burnt_food)
        self.drop(slots)
        self.done += len(slots)
        self.log_msg(f"Fished and dropped: ~{self.done}")
        time.sleep(1)
        