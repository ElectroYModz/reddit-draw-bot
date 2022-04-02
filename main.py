# imports
import os
import math
import requests
import json
import time
import threading
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from PIL import ImageColor
from PIL import Image
import random

# load env variables
load_dotenv()

# auth variables
access_token = None
access_token_expires_at_timestamp = math.floor(time.time())

# place a pixel immediately
first_run = True

# method to draw a pixel at an x, y coordinate in r/place with a specific color
def set_pixel(access_token_in, x, y, color_index_in=18, canvas_index=0):
    print("placing pixel with color index " + str(color_index_in) + " at " + str((x, y)))

    url = "https://gql-realtime-2.reddit.com/query"

    payload = json.dumps({
        "operationName": "setPixel",
        "variables": {
            "input": {
                "actionName": "r/replace:set_pixel",
                "PixelMessageData": {
                    "coordinate": {
                        "x": x,
                        "y": y
                    },
                    "colorIndex": color_index_in,
                    "canvasIndex": canvas_index
                }
            }
        },
        "query": "mutation setPixel($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n            __typename\n          }\n          ... on SetPixelResponseMessageData {\n            timestamp\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
    })
    headers = {
        'origin': 'https://hot-potato.reddit.com',
        'referer': 'https://hot-potato.reddit.com/',
        'apollographql-client-name': 'mona-lisa',
        'Authorization': 'Bearer ' + access_token_in,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print("received response: ", response.text)
    print("X: %s, Y: %s, Color: %s"%(x, y, color_index_in))

# task to draw the input image
def task(credentials_index):
    # whether image should keep drawing itself
    repeat_forever = True

    while True:
        try:
            # global variables for script
            last_time_placed_pixel = math.floor(time.time())

            # note: reddit limits us to place 1 pixel every 5 minutes, so I am setting it to
            # 5 minutes and 30 seconds per pixel
            pixel_place_frequency = 330

            # string for time until next pixel is drawn
            update_str = ""

            # reference to globally shared variables such as auth token and image
            global access_token
            global access_token_expires_at_timestamp

            # boolean to place a pixel the moment the script is first run
            global first_run

            # refresh auth tokens and / or draw a pixel
            while True:
                # get the current time
                current_timestamp = math.floor(time.time())
                
                # log next time until drawing
                time_until_next_draw = last_time_placed_pixel + pixel_place_frequency - current_timestamp
                new_update_str = str(time_until_next_draw) + " seconds until next pixel is drawn"
                if update_str != new_update_str:
                    update_str = new_update_str
                    print("__________________")
                    print("Thread #" + str(credentials_index))
                    print(update_str)
                    print("__________________")
                # refresh access token if necessary
                if access_token is None or current_timestamp >= access_token_expires_at_timestamp:
                    print("__________________")
                    print("Thread #" + str(credentials_index))
                    print("refreshing access token...")

                    # developer's reddit username and password
                    username = json.loads(os.getenv('ENV_PLACE_USERNAME'))[credentials_index]
                    password = json.loads(os.getenv('ENV_PLACE_PASSWORD'))[credentials_index]
                    # note: use https://www.reddit.com/prefs/apps
                    app_client_id = json.loads(os.getenv('ENV_PLACE_APP_CLIENT_ID'))[credentials_index]
                    secret_key = json.loads(os.getenv('ENV_PLACE_SECRET_KEY'))[credentials_index]

                    data = {
                        'grant_type': 'password',
                        'username': username,
                        'password': password
                    }
                    
                    r = requests.post("https://ssl.reddit.com/api/v1/access_token",
                                      data=data,
                                      auth=HTTPBasicAuth(app_client_id, secret_key),headers={'User-agent': f'placebot{random.randint(1,100000)}'})

                    print("received response: ", r.text)

                    response_data = r.json()
                    access_token = response_data["access_token"]
                    # access_token_type = response_data["token_type"]  # this is just "bearer"
                    access_token_expires_in_seconds = response_data["expires_in"]  # this is usually "3600"
                    # access_token_scope = response_data["scope"]  # this is usually "*"

                    # ts stores the time in seconds
                    access_token_expires_at_timestamp = current_timestamp + int(access_token_expires_in_seconds)

                    print("received new access token: ", access_token)
                    print("__________________")

                # draw pixel onto screen
                if access_token is not None and (current_timestamp >= last_time_placed_pixel + pixel_place_frequency
                                                 or first_run):
                    # place pixel immediately
                    first_run = False

                    # draw the pixel onto r/place
                    x = requests.get('http://place.cokesniffer.org/next.json')
                    nextData = x.json()
                    set_pixel(access_token, nextData['x'], nextData['y'], nextData['color'])
                    last_time_placed_pixel = math.floor(time.time())
        except:
            print("__________________")
            print("Thread #" + str(credentials_index))
            print("Error refreshing tokens or drawing pixel")
            print("Trying again in 5 minutes...")
            print("__________________")
            time.sleep(5 * 60)

        if not repeat_forever:
            break

# get number of concurrent threads to start
num_credentials = len(json.loads(os.getenv('ENV_PLACE_USERNAME')))

for i in range(num_credentials):
    # run the image drawing task
    thread1 = threading.Thread(target=task, args=[i])
    thread1.start()
