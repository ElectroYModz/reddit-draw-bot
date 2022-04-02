#!/usr/bin/env python3

import os
import os.path
import math
import json
import time
import threading
import logging
import argparse
from io import BytesIO
import random
from urllib import response
import requests
import colorama
from websocket import create_connection
from requests.auth import HTTPBasicAuth

from mappings import color_map, name_map

# Option remains for legacy usage
# equal to running
# python main.py --verbose
verbose_mode = False



class PlaceClient:
    def __init__(self):
        # Data
        self.json_data = self.get_json_data()

        # In seconds
        self.delay_between_launches = (
            self.json_data["thread_delay"]
            if self.json_data["thread_delay"] != None
            else 3
        )

        # Auth
        self.access_tokens = {}
        self.access_token_expires_at_timestamp = {}

        self.first_run_counter = 0

        self.load_proxies()
    """ Utils """
    # Convert rgb tuple to hexadecimal string

    def get_json_data(self):
        if not os.path.exists("config.json"):
            exit("No config.json file found. Read the README")

        # To not keep file open whole execution time
        f = open("config.json")
        json_data = json.load(f)
        f.close()

        return json_data

    """ Main """
    # Draw a pixel at an x, y coordinate in r/place with a specific color

    def set_pixel_and_check_ratelimit(
        self, index, access_token_in, x, y, color_index_in=18, canvas_index=0
    ):
        logging.info(
            f"Attempting to place {color_index_in} pixel at {x}, {y}"
        )

        if x > 1000 or y > 1000:
            canvas_index = 1
            if x > 1000: x -= 1000
            if y > 1000: y -= 1000
        else:
         canvas_index = 0

        url = "https://gql-realtime-2.reddit.com/query"

        payload = json.dumps(
            {
                "operationName": "setPixel",
                "variables": {
                    "input": {
                        "actionName": "r/replace:set_pixel",
                        "PixelMessageData": {
                            "coordinate": {"x": x, "y": y},
                            "colorIndex": color_index_in,
                            "canvasIndex": canvas_index,
                        },
                    }
                },
                "query": "mutation setPixel($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n            __typename\n          }\n          ... on SetPixelResponseMessageData {\n            timestamp\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            }
        )
        headers = {
            "origin": "https://hot-potato.reddit.com",
            "referer": "https://hot-potato.reddit.com/",
            "apollographql-client-name": "mona-lisa",
            "Authorization": "Bearer " + access_token_in,
            "Content-Type": "application/json",
        }

        response = requests.request("POST", url, headers=headers, data=payload, proxies=self.get_proxy_to_use(index))
        logging.debug(f"Received response: {response.text}")

        # There are 2 different JSON keys for responses to get the next timestamp.
        # If we don't get data, it means we've been rate limited.
        # If we do, a pixel has been successfully placed.
        if response.json()["data"] is None:
            logging.info(response.json())

            waitTime = math.floor(
                response.json()["errors"][0]["extensions"]["nextAvailablePixelTs"]
            )
            logging.info(
                f"{colorama.Fore.RED}Failed placing pixel: rate limited {colorama.Style.RESET_ALL}"
            )
        else:
            waitTime = math.floor(
                response.json()["data"]["act"]["data"][0]["data"][
                    "nextAvailablePixelTimestamp"
                ]
            )
            logging.info(
                f"{colorama.Fore.GREEN}Succeeded placing pixel {colorama.Style.RESET_ALL}"
            )

        # THIS COMMENTED CODE LETS YOU DEBUG THREADS FOR TESTING
        # Works perfect with one thread.
        # With multiple threads, every time you press Enter you move to the next one.
        # Move the code anywhere you want, I put it here to inspect the API responses.

        # import code

        # code.interact(local=locals())

        # Reddit returns time in ms and we need seconds, so divide by 1000
        return waitTime / 1000

    def load_proxies(self):
        lis = open('proxies.txt', 'r').read().splitlines()
        
        
        if(len(self.proxies) == 0):
            logging.info("No proxies found. Using direct connection.")
            self.proxies = []

    def get_proxy_to_use(self, index):
        if len(self.proxies) == 0:
            return ''
        proxy_index = index / 2
        overflow_amount = proxy_index / len(self.proxies) 

        if overflow_amount > 1:
            proxy_index = proxy_index % len(self.proxies)

        return {'https': self.proxies[int(proxy_index)]}
        


    # Draw the input image
    def task(self, index, name, worker):
        # Whether image should keep drawing itself
        repeat_forever = True

        while True:
            # last_time_placed_pixel = math.floor(time.time())

            # note: Reddit limits us to place 1 pixel every 5 minutes, so I am setting it to
            # 5 minutes and 30 seconds per pixel
            pixel_place_frequency = 40

            next_pixel_placement_time = math.floor(time.time()) + pixel_place_frequency

            try:
                # Current pixel row and pixel column being drawn
                current_r = worker["start_coords"][0]
                current_c = worker["start_coords"][1]
            except Exception:
                print(
                    f"You need to provide start_coords to worker '{name}'",
                )
                exit(1)

            # Time until next pixel is drawn
            update_str = ""

            # Refresh auth tokens and / or draw a pixel
            while True:
                # reduce CPU usage
                time.sleep(1)

                # get the current time
                current_timestamp = math.floor(time.time())

                # log next time until drawing
                time_until_next_draw = next_pixel_placement_time + pixel_place_frequency

                new_update_str = (
                    f"{(time_until_next_draw - current_timestamp)} seconds until next pixel is drawn"
                )
                if update_str != new_update_str:
                    update_str = new_update_str

                logging.info(f"Thread #{index} :: {update_str}")

                # refresh access token if necessary
                # print("TEST:", self.access_token_expires_at_timestamp, "INDEX:", index)
                if (
                    len(self.access_tokens) == 0
                    or len(self.access_token_expires_at_timestamp) == 0
                    or
                    # index in self.access_tokens
                    index not in self.access_token_expires_at_timestamp
                    or (
                        self.access_token_expires_at_timestamp.get(index)
                        and current_timestamp
                        >= self.access_token_expires_at_timestamp.get(index)
                    )
                ):
                    logging.info(f"Thread #{index} :: Refreshing access token")

                    # developer's reddit username and password
                    try:
                        username = name
                        password = worker["password"]
                        # note: use https://www.reddit.com/prefs/apps
                        app_client_id = worker["client_id"]
                        secret_key = worker["client_secret"]
                    except Exception:
                        print(
                            f"You need to provide all required fields to worker '{name}'",
                        )
                        exit(1)

                    data = {
                        "grant_type": "password",
                        "username": username,
                        "password": password,
                    }

                    r = requests.post(
                        "https://ssl.reddit.com/api/v1/access_token",
                        data=data,
                        auth=HTTPBasicAuth(app_client_id, secret_key),
                        headers={"User-agent": f"placebot{random.randint(1, 100000)}"},
                        proxies=self.get_proxy_to_use(index),
                    )

                    logging.debug(f"Received response: {r.text}")

                    response_data = r.json()

                    if "error" in response_data:
                        print(
                            f"An error occured. Make sure you have the correct credentials. Response data: {response_data}"
                        )
                        exit(1)

                    self.access_tokens[index] = response_data["access_token"]
                    # access_token_type = response_data["token_type"]  # this is just "bearer"
                    access_token_expires_in_seconds = response_data[
                        "expires_in"
                    ]  # this is usually "3600"
                    # access_token_scope = response_data["scope"]  # this is usually "*"

                    # ts stores the time in seconds
                    self.access_token_expires_at_timestamp[
                        index
                    ] = current_timestamp + int(access_token_expires_in_seconds)

                    logging.info(
                        f"Received new access token: {self.access_tokens.get(index)[:5]}************"
                    )

                # draw pixel onto screen
                if self.access_tokens.get(index) is not None and (
                    current_timestamp
                    >= next_pixel_placement_time + pixel_place_frequency
                    or self.first_run_counter <= index
                ):

                    # place pixel immediately
                    # first_run = False
                    self.first_run_counter += 1

                    # get target color
                    # target_rgb = pix[current_r, current_c]

                    # get the pixel data from the api
                    pixelData = requests.get('http://place.cokesniffer.org/next.json', headers={"X-Requested-With":"Reddit /r/place 2b2t Bot"}).json()

                    # draw the pixel onto r/place
                    next_pixel_placement_time = self.set_pixel_and_check_ratelimit(index,
                        self.access_tokens[index],
                        pixelData['x'],
                        pixelData['y'],
                        pixelData['color'],
                    )

            if not repeat_forever:
                break

    def start(self):
        for index, worker in enumerate(self.json_data["workers"]):
            threading.Thread(
                target=self.task,
                args=[index, worker, self.json_data["workers"][worker]],
            ).start()
            # exit(1)
            time.sleep(self.delay_between_launches)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    colorama.init()
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=(logging.DEBUG if verbose_mode else args.loglevel),
        format="[%(asctime)s] :: [%(levelname)s] - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )
    logging.info("place-script started")

    client = PlaceClient()
    # Start everything
    client.start()
