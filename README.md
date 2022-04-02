# Reddit Drawing Bot Running Instructions

## Setting up the requirements

Download the Python installer from [here](https://www.python.org/downloads/release/python-398/)
Make sure "Add Python 3.9 to PATH is ticked
Click on Customize installation, and make sure everything is ticked
Click on "Next"
Make sure "Add Python to environment variables" is ticked"
Click install. and let it go
 


## Running the bot

To run it first install the requirements with pip install -r requirements.txt

### Filling up config.json:

Get client id and secret key [here](https://www.reddit.com/prefs/apps) scroll down and click the button that says "are you a developer? create an app... or create another", and create a **SCRIPT**

`worker1username` is the username of the first woker account (**DO NOT TOUCH THE DOUBLE QUOTES**)  
`password` is the password of the worker account(**EDIT THE ONE AFTER THE COLON, SAME AS ABOVE**)  
`client_id` is the client id of the script, the one right under the name you gave the script  
`clientsecret` is the secret key of the script

**NOTE: do the same for the second worker and so on, make sure to place the curly brackets right**

**start_coords ARE IGNORED, DO NOT MODIFY THEM**

Then simply double click main.py

