# Spotify Connect Controller

An Alexa voice skill running on an AWS Lambda instance that interfaces with the Spotify API to control and switch playback on any available Spotify Connect devices.

Examples:
* "Alexa, ask Spotify Connect to list my devices"
* "Alexa, ask Spotify Connect to switch to my phone"
* "Alexa, ask Spotify Connect to pause"

## Setup
I'm currently working on getting this skill released to the Alexa skill store, but in the meantime you can set it up to test it out on your personal Echo devices!

1. Register for [Amazon](https://developer.amazon.com/alexa/) and [Spotify](https://developer.spotify.com/dashboard/) developer accounts. Create an empty Alexa custom skill and a Spotify developer app, but don't make any changes yet.

2. On the build page of the Alexa skill, copy the contents of `interaction_model.json` into the JSON Editor on the left sidebar.

3. Go to the 'Account Linking' tab. Enable the first option and make sure both settings are disabled. Select Auth Code Grant for the authorization grant type, with the following information:
    * Authorization URI: `https://accounts.spotify.com/authorize`
    * Access Token URI: `https://accounts.spotify.com/api/token`
    * Client ID: Client ID of the Spotify Developer app
    * Client secret: Client secret of the Spotify Developer app
    * Authentication Scheme: HTTP Basic
    * Scopes: `user-modify-playback-state`, `user-read-playback-state`
    
    Copy the three Redirect URLs listed at the bottom of the page.
    
 4. On the Spotify Developer page for the app you've created, click 'Edit Settings'. Under the 'Redirect URIs' section, paste the three URLs you copied earlier.
 
 5. [Create a Lambda function using the Python 3.7 runtime](https://developer.amazon.com/en-US/docs/alexa/custom-skills/host-a-custom-skill-as-an-aws-lambda-function.html#create-a-lambda-function-from-scratch) and [link it to your Alexa custom skill.](https://developer.amazon.com/fr-FR/docs/alexa/custom-skills/host-a-custom-skill-as-an-aws-lambda-function.html#connect-to-skill)
 
 6. Clone this repository and set up a Python 3 virtual environment in the directory: `python3 -m venv /path/to/new/virtual/environment`
 
 7. Activate the virtual environment and install `json` and `requests` with pip.
 
 8. Assuming your environment is called `venv`, `cd` into `venv/lib/python3.7/site-packages` and run `zip -r9 your_original_folder_path/function.zip .`
 
 9. `cd` back to the base directory and add lambda_function.py to the zip with `zip -g function.zip lambda_function.py`
 
 10. On the Lambda function page, upload function.zip and click save. Happy testing!
