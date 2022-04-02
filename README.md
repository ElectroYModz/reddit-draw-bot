# Reddit Drawing Bot Running Instructions

## Setting up the requirements

1. Download the Python installer from [here](https://www.python.org/downloads/release/python-398/)  
2. Make sure "Add Python 3.9 to PATH is ticked  
3. Click on Customize installation, and make sure everything is ticked  
4. Click on "Next"  
5. Make sure "Add Python to environment variables" is ticked"  
6. Click install. and let it go  
 


## Python Package Requirements

To run the bot for the first time, install the requirements.
### Windows

```shell
pip install -r requirements.txt
```
simply open the directory you've extracted the bot to, and type `cmd` in the address bar like so:
![explorer_Jj87pVSbCj](https://user-images.githubusercontent.com/67830794/161401653-72fa3f27-0bd1-4863-89bc-cd13d8e4ecc6.gif)

### Other OS

Ideally, cd into the directory and run the following command:
```shell
pip3 install -r requirements.txt
```
### MacOSX hot fix
If you are using MacOSX and encounter an SSL_CERTIFICATE error. Please apply the fix detailed https://stackoverflow.com/questions/42098126/mac-osx-python-ssl-sslerror-ssl-certificate-verify-failed-certificate-verify  



## Filling up config.json:

Get client id and secret key [here](https://www.reddit.com/prefs/apps) scroll down and click the button that says "are you a developer? create an app... or create another", and create a **SCRIPT**  
![firefox_z3p85Q0UES](https://user-images.githubusercontent.com/67830794/161401978-72b1cce1-bfba-4926-91bd-5922e61e484f.png)

![image](https://user-images.githubusercontent.com/67830794/161402003-85368d98-fb8c-4949-82f3-30addf5dbe23.png)



`worker1username` is the username of the first woker account (**DO NOT TOUCH THE DOUBLE QUOTES**)  
`password` is the password of the worker account(**EDIT THE ONE AFTER THE COLON, SAME AS ABOVE**)  
`client_id` is the client id of the script, the one right under the name you gave the script  
`clientsecret` is the secret key of the script

**NOTE: do the same for the second worker and so on, make sure to place the curly brackets right**

**start_coords ARE IGNORED, DO NOT MODIFY THEM**

## Running the Script
simply double click main.py

