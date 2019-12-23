import json
import random
import requests

class SpotifyConnector:
    def __init__(self, access_token):
        #Alexa handles account linking thru auth grant flow and sends access
        #token with each request
        self.auth_token = access_token
        self.devices = self.refresh_device_hash()

    def make_basic_auth(self):
        return {"Authorization": "Basic " + self.client_encoded}

    def make_bearer_auth(self):
        return {"Authorization": "Bearer " + self.auth_token}

    def refresh_device_hash(self, previous_url=None, previous_payload=None):
        #represent ids by device and type so users can specify either
        devices = { 'name': {}, 'type': {}}
        bearer_auth = self.make_bearer_auth()
        device_list_response = requests.get("https://api.spotify.com/v1/me/player/devices", headers=bearer_auth)
        device_list = device_list_response.json()['devices']
        for device in device_list:
            devices['name'][device['name']] = device['id']
            devices['type'][device['type']] = device['id']
        if(previous_url or previous_payload):
            return make_action_and_confirm(previous_url, previous_payload)
        return devices

    def make_action_and_confirm(self, url, payload=None):
        # TODO: Error handling in class functions instead, which return
        # appropriate responses
        auth_header = self.make_bearer_auth()
        r = requests.put(url, headers=auth_header, data=payload)
        if(r.status_code == 204 or r.status_code == 200):
            return True
        elif(r.status_code == 404):
            reason = r.json()['error']['reason']
            if reason == "NO_ACTIVE_DEVICE":
                return False
        elif(r.status_code == 403):
            reason = r.json()['error']['reason']
            if reason == "PREMIUM_REQUIRED":
                return False
        else:
            return False
        return False

    def make_play_request(self, device=None):
        device_id = None
        if(device != None):
            print(device)
            device_id = self.__find_device(device)
        if(device_id != None):
            url = "https://api.spotify.com/v1/me/player/play?device_id="+device_id
        else:
            url = "https://api.spotify.com/v1/me/player/play"
        return self.make_action_and_confirm(url)

    def make_pause_request(self):
        return self.make_action_and_confirm("https://api.spotify.com/v1/me/player/pause")

    def __find_device(self, device=""):
        names = self.devices["name"]
        types = self.devices["type"]
        for k in names.keys():
            if(device.lower() in k.lower()):
                return names[k]
        for k in types.keys():
            if(device.lower() in k.lower()):
                return types[k]
        return None

    def make_switch_device_request(self, device):
        device_id = self.__find_device(device)
        if(device_id == None):
            return False
        payload = json.dumps({"device_ids":[device_id]})
        return self.make_action_and_confirm("https://api.spotify.com/v1/me/player", payload)

    def list_devices(self):
        if not self.devices:
            self.devices = self.refresh_device_hash()
        device_names = list(self.devices['name'].keys())
        device_types = list(self.devices['type'].keys())
        num_devices = len(device_names)
        response = f"""Spotify Connect has {num_devices} available {"device. Its name and type is" if (num_devices == 1) else "devices. Their names and types are"}"""
        for i in range(num_devices-1):
            device = f" {device_names[i]}, a {device_types[i]};"
            response += device
        if num_devices != 1:
            response += " and"
        response += f""" {device_names[-1]}, a {device_types[-1]}.
        You can use any part of a device's name or type to control it."""
        return response

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

def build_card_response(dialog, card_type):
    response = build_response(dialog)
    response.update({"card": {"type": card_type}})
    return response

def handle_intent(request, token):
    sc = SpotifyConnector(token)
    intent_name = request["intent"]["name"]
    if(intent_name == "PlayIntent"):
        #TODO: add arg here to specify which device to play on?
        if("value" in request["intent"]["slots"]["deviceName"]):
            device_name = request["intent"]["slots"]["deviceName"]["value"]
            action_confirmed = sc.make_play_request(device_name)
        else:
            action_confirmed = sc.make_play_request()
        if(action_confirmed):
            return build_response("Playing")
        else:
            return build_response("There was an error. Please retry in a second.")
    elif(intent_name == "PauseIntent"):
        action_confirmed = sc.make_pause_request()
        if(action_confirmed):
            return build_response("Paused")
        else:
            return build_response("There was an error. Please retry in a second.")
    elif(intent_name == "ListDevicesIntent"):
        device_response = sc.list_devices()
        return build_response(device_response)
    elif(intent_name == "SwitchDeviceIntent"):
        device_name = request["intent"]["slots"]["deviceName"]["value"]
        action_confirmed = sc.make_switch_device_request(device_name)
        if(action_confirmed):
            return build_response("Now playing on " + device_name)
        else:
            return build_response("I couldn't find that device. Try asking what your devices are.")

def access_token(event):
    context = event["context"]
    if("accessToken" in context["System"]["user"]):
        #TODO: verify that access token is valid (does spotify have a way to check this?)
        return context["System"]["user"]["accessToken"]
    return None

def lambda_handler(event, context):
    token = access_token(event)
    if(token != None):
        if(event["request"]["type"] == "IntentRequest"):
            return handle_intent(event["request"], token)
        else:
            return build_response("Please specify an action.")
    else:
        return build_card_response("Please use the Alexa app on your phone to link your Spotify account to this skill.", "LinkAccount")
