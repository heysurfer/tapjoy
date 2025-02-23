import datetime
import hashlib
import json
import random
from urllib.parse import quote, urlparse
import time
import uuid
from misc.misc import create_timestamp, generate_random_string, generate_unique_uuid
from offer.offerStruct import offerStruct
from httpClient.httpClient import httpClient
from datetime import datetime, timezone
import logging

def generate_device_info():
    device_names = [
        "iPhone14,2", "iPhone14,3", "iPhone14,4", "iPhone14,5",
        "iPhone14,6", "iPhone14,7", "iPhone14,8", "iPhone15,2",
        "iPhone15,3", "iPhone15,4", "iPhone15,5"
    ]
    
    hardware_names = [
        "D17AP", "D27AP", "D16AP", "D26AP",
        "D63AP", "D64AP", "D28AP", "D73AP",
        "D74AP", "D75AP", "D76AP"
    ]
    
    device_manufacturers = [
        "Apple", "Apple Inc.", "Apple Computer, Inc."
    ]
    
    os_builds = [
        "20D47", "20D67", "20E247", "20E252",
        "20F66", "20F67", "20G75"
    ]
    
    device_name = random.choice(device_names)
    hardware_name = random.choice(hardware_names)
    manufacturer = random.choice(device_manufacturers)
    os_build = random.choice(os_builds)
    
    return {
        "device_name": device_name,
        "hardware_name": hardware_name,
        "device_manufacturer": manufacturer,
        "os_build": os_build
    }

class AdjustApi:
    def __init__(self, ad_id, proxy_str, offer_data: offerStruct):
        self.ad_id = ad_id
        self.session = httpClient(proxy_str=proxy_str)
        self.api = "https://app.adjust.net.in"
        self.uuid = str(uuid.uuid1())
        self.offerData = offer_data
        self.google_app_set_id = generate_unique_uuid()
        self.device_id = generate_random_string(32)
        self.google_id = generate_unique_uuid()
        self.current_cap = 0
        self.session.headers.update({
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
            "Client-SDK": "unity4.35.2@android4.35.1",
            "Connection": "close",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded",
        })
        self.deviceInformation = generate_device_info()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def createAuthorization(self, created_at, activity_kind, app_secret):
        if len(app_secret) == 0:
            return ''
        withoutSecret = app_secret[1:]
        sign = hashlib.sha256(f"{created_at}{self.ad_id}{withoutSecret}{activity_kind}".encode()).hexdigest().lower()
        authorization = f'Signature secret_id="{app_secret[0]}",signature="{sign}",algorithm="sha256",headers="created_at gps_adid app_secret activity_kind"'
        return authorization

    def createSession(self):
        self.logger.debug("Creating session")
        formatted_utc_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z-0500'
        url_encoded_timestamp = quote(formatted_utc_timestamp)
        callback_params = {"nakama.deviceId": self.device_id}
        callback_params_json = json.dumps(callback_params)
        encoded_callback_params = quote(callback_params_json)
        data = {
            "updated_at": create_timestamp(),
            "device_type": "phone",
            "device_manufacturer": self.deviceInformation["device_manufacturer"],
            "gps_adid": self.ad_id,
            "google_app_set_id": self.google_id,
            "environment": "production",
            "session_count": 1,
            "android_uuid": self.uuid,
            "attribution_deeplink": 1,
            "connectivity_type": 1,
            "os_build": self.deviceInformation["os_build"],
            "api_level": 28,
            "needs_response_details": 1,
            "event_buffering_enabled": 0,
            "mcc": 286,
            "os_name": "android",
            "display_width": 720,
            "screen_format": "long",
            "screen_density": "high",
            "hardware_name": self.deviceInformation["hardware_name"],
            "tracking_enabled": 1,
            "gps_adid_src": "service",
            "package_name": "hangout.knka_gl0",
            "mnc": 1,
            "app_version": "2.0.13",
            "installed_at": create_timestamp(),
            "country": "US",
            "gps_adid_attempt": 1,
            "screen_size": "large",
            "app_token": self.offerData.offerToken,
            "ui_mode": 1,
            "device_name": "22081212C",
            "display_height": 1280,
            "created_at": create_timestamp(),
            "language": "en",
            "os_version": "7.1.2",
            "cpu_type": "x86_64",
            "sent_at": create_timestamp()
        }
        self.session.headers.update({
            "Authorization": self.createAuthorization(data["created_at"], "session", self.offerData.secretKey)
        })
        if self.offerData.secretKey != "":
            data["app_secret"] = self.offerData.secretKey[1:]
        try:
            response = self.session.post(f"{self.api}/session", data=data)
            print(response.text)
            response.raise_for_status()
            self.logger.debug("Session created successfully.")
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")

    def attribution(self):
        self.logger.debug("Starting attribution")
        formatted_utc_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z-0500'
        query_params = {
            "device_type": "phone",
            "gps_adid": self.ad_id,
            "google_app_set_id": self.google_id,
            "environment": "production",
            "attribution_deeplink": 1,
            "android_uuid": self.uuid,
            "gps_adid_src": "service",
            "tracking_enabled": 1,
            "package_name": "hangout.knka_gl0",
            "initiated_by": "backend",
            "app_version": "2.0.13",
            "api_level": 28,
            "needs_response_details": 1,
            "gps_adid_attempt": 1,
            "app_token": self.offerData.offerToken,
            "device_name": self.deviceInformation["device_name"],
            "ui_mode": 1,
            "created_at": create_timestamp(),
            "event_buffering_enabled": 0,
            "os_version": "7.1.2",
            "os_name": "android",
            "sent_at": create_timestamp()
        }

        if self.offerData.secretKey != "":
            query_params["app_secret"] = self.offerData.secretKey[1:]
        self.session.headers.update({
            "Authorization": self.createAuthorization(query_params["created_at"], "attribution", self.offerData.secretKey)
        })
        response = self.session.get(f"{self.api}/attribution", params=query_params)
        print(response.text)
        network = response.json()["attribution"]['network']
        self.logger.debug("Attribution completed")
        return "Tapjoy" in network
    
    def sendEvent(self, eventValue, extraData=None):
        data = {
            "device_type": "phone",
            "device_manufacturer": self.deviceInformation["device_manufacturer"],
            "gps_adid": self.ad_id,
            "environment": "production",
            "session_count": "1",
            "android_uuid": self.uuid,
            "hardware_name": self.deviceInformation["hardware_name"],
            "device_name": self.deviceInformation["device_name"],
            "app_token": self.offerData.offerToken,
            "screen_density": "high",
            "attribution_deeplink": 1,
            "session_count": 1,
            "display_height": 1600,
            "package_name": "com.MachinaGames.CardQuest",
            "os_name": "android",
            "ui_mode": 1,
            "tracking_enabled": 1,
            "sent_at": create_timestamp(),
            "queue_size": 1,
            "needs_response_details": 1,
            "os_build": self.deviceInformation["os_build"],
            "cpu_type": "x86_64",
            "screen_size": "normal",
            "screen_format": "long",
            "gps_adid_src": "service",
            "subsession_count": 1,
            "mnc": "01",
            "os_version": 9,
            "time_spent": 5878,
            "created_at": create_timestamp(),
            "event_token": eventValue
        }
        if extraData:
            data.update(extraData)
        if self.offerData.secretKey != "":
            data["app_secret"] = self.offerData.secretKey[1:]
        if self.offerData.isDaily:
            self.current_cap += 1
            strFormat = str(self.current_cap)
            data["event_token"] = self.offerData.offerEventTokens[0]
            data["partner_params"] = '{"level_complete":"' + strFormat + '"}'
            data["callback_params"] = '{"levelNumber":"' + strFormat + '"}'
            if self.offerData.offerName == "Wordle!":
                data["callback_params"] = '{"sixguesses_complete":"'+ strFormat +'"}'
            if self.offerData.offerName == "Decor Merge - Fashion Renovate":
                data["callback_params"] = '{"level_id":"1_mission_'+str(100000+self.current_cap)+'"}'
        self.session.headers.update({
            "Authorization": self.createAuthorization(data["created_at"], "event", self.offerData.secretKey) 
        })
        response = self.session.post(f"{self.api}/event", data=data)
        try:
            response_json = response.json()
            if 'error' in response_json:
                self.logger.error(f"Event send failed with error: {response_json['error']}")
                return False
            return True
        except json.JSONDecodeError:
            self.logger.error("Failed to parse response JSON")
            return False
        if response.status_code != 200:
            self.logger.error(f"Event send failed with status code: {response.status_code}")
            return False
        else:
            return True