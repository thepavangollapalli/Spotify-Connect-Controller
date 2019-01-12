import json
from botocore.vendored import requests

# Follow https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow
# Obtain a client id/secret and refresh token
client_encoded = ""
auth_token = ""
refresh_token = ""

spotify_api_url = "https://api.spotify.com/v1/me/player/"

# GET https://api.spotify.com/v1/me/player/devices for device ids
# Note: device id refreshes on device restart
devices = {"laptop":"",
            "phone":"",
            "tv":"",
            "echo":""}

def build_response(dialog):
    return {
      "version": "1.0",
      "sessionAttributes": {},
      "response": {
        "outputSpeech": {
          "type": "PlainText",
          "text": dialog,
          "playBehavior": "REPLACE_ENQUEUED"      
            },
        },
        "shouldEndSession": True
     }
     
def refresh_auth(previous_url=None, previous_payload=None):
    basic_auth = {"Authorization": "Basic " + client_encoded}
    refresh_payload = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    renew = requests.post("https://accounts.spotify.com/api/token", headers=basic_auth, data=refresh_payload)
    if(renew.status_code == 200):
        global auth_token = renew.json()["access_token"]
    if(previous_url or previous_payload):
        return make_action_and_confirm(previous_url, previous_payload)

def make_action_and_confirm(url, payload=None):
    auth_header = {"Authorization": "Bearer " + auth_token}
    response = requests.put(url, headers=auth_header, data=payload) 
    if(response.status_code == 204):
        return True
    elif(response.status_code == 401):
        print("refreshing auth")
        refresh_auth(url, payload)
    else:
        print(response.status_code, response.text)
        return False
    
def handle_intent(request):
    intent_name = request["intent"]["name"]
    if(intent_name == "PlayIntent"):
        action_confirmed = make_action_and_confirm(spotify_api_url + "play")
        if(action_confirmed):
            return build_response("Playing")
    elif(intent_name == "PauseIntent"):
        action_confirmed = make_action_and_confirm(spotify_api_url + "pause")
        if(action_confirmed):
            return build_response("Paused")
    elif(intent_name == "SwitchDeviceIntent"):
        device_name = request["intent"]["slots"]["deviceName"]["value"].lower()
        device_id = devices[device_name]
        payload = {"device_ids":[device_id]}
        action_confirmed = make_action_and_confirm(spotify_api_url, json.dumps(payload))
        if(action_confirmed):
            return build_response("Now playing on " + device_name)
    return build_response("There was an error. Please retry in a second.")

def lambda_handler(event, context):
    refresh_auth()
    if(event["request"]["type"] == "IntentRequest"):
        return handle_intent(event["request"])
    else:
        return build_response("Please specify an action.")
