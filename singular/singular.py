import hashlib
import json
import time
import uuid
from misc.misc import generate_random_string, generate_unique_uuid
from offer.offerStruct import offerStruct
from httpClient.httpClient import httpClient

class SingularApi:
    offerData: offerStruct

    def __init__(self, ad_id, proxy_str, offer_data: offerStruct):
        self.ad_id = ad_id
        self.session = httpClient(proxy_str=proxy_str, user_agent="Singular/SDK-v12.5.5.PROD")
        self.api = "https://sdk-api-v1.singular.net/api/v1/"
        self.uuid = str(uuid.uuid1())
        self.offerData = offer_data
        self.google_app_set_id = generate_unique_uuid()
        self.device_id = generate_random_string(32)
        self.google_id = generate_unique_uuid()

    def sha1_hash(self, str1: str):
        try:
            sha1 = hashlib.sha1()
            sha1.update(self.offerData.secretKey.encode('utf-8'))
            sha1.update(str1.encode('utf-8'))
            return sha1.hexdigest()
        except Exception:
            return None
    
    def createSession(self):
        unix_time = int(time.time())

        query = (
            f"?a={self.offerData.apiKey}&p=Android&u={self.ad_id}&i={self.offerData.packageName}"
            f"&k=AIFA&sdk=Singular%2Fv12.5.5-Unity%2F4.4.2&aifa={self.ad_id}"
        )
        resolve_url = self.api + "resolve" + query + f"&h=" + self.sha1_hash(query)
        self.session.post(resolve_url, json={})

        start_query = (
            f"?a={self.offerData.apiKey}&ab=x86_64&aifa={self.ad_id}&asid_scope=1&asid_timeinterval=0.084"
            f"&av=2.13.0&br=samsung&c=wifi&current_device_time={unix_time}"
            f"&custom_user_id={self.google_id}&ddl_enabled=true&ddl_to=60&de=gracelte"
            f"&device_type=phone&device_user_agent=Dalvik%2F2.1.0+%28Linux%3B+U%3B+Android+9%3B+SM-G977N+Build%2FPQ3A.190705.08211809%29"
            f"&dnt=0&event_index=0&i={self.offerData.packageName}&install_ref=%7B%22installBeginTimestampSeconds%22%3A0"
            f"%2C%22referrer%22%3A%22utm_source%3Dgoogle-play%26utm_medium%3Dorganic%22%2C%22installBeginTimestampServerSeconds%22%3A0"
            f"%2C%22clickTimestampSeconds%22%3A0%2C%22referrer_source%22%3A%22service%22%2C%22clickTimestampServerSeconds%22%3A0"
            f"%2C%22current_device_time%22%3A1734149342156%2C%22installVersion%22%3Anull%7D"
            f"&install_ref_timeinterval=0.13&install_time=1734144651465&is=true&k=AIFA&lag=0.848"
            f"&lc=en_US&ma=samsung&mo=SM-G977N&n=Color+Wall&p=Android&pr=SM-G977N"
            f"&rt=json&s={unix_time}&sdk=Singular%2Fv12.5.5-Unity%2F4.4.2"
            f"&singular_install_id={self.device_id}2&src=com.android.coreservice&u={self.ad_id}"
            f"&update_time={unix_time}&v=9"
        )
        start_url = self.api + "start" + start_query + f"&h=" + self.sha1_hash(start_query)
        self.session.post(
            start_url,
            json={
                "payload": "{\"referrer_data\":\"{}\"}",
                "signature": self.sha1_hash("{\"referrer_data\":\"{}\"}")
            }
        )

        event_query = (
            f"?a={self.offerData.apiKey}&aifa={self.ad_id}&av=2.13.0&c=wifi"
            f"&custom_user_id={self.google_id}&event_index=1&i={self.offerData.packageName}&k=AIFA"
            f"&lag=0.498&n=__LicensingStatus&p=Android&rt=json&s={unix_time}"
            f"&sdk=Singular%2Fv12.5.5-Unity%2F4.4.2&seq=1&singular_install_id={self.device_id}"
            f"&t=2.8850000000000002&u={self.ad_id}"
        )
        event_url = self.api + "event" + event_query + f"&h=" + self.sha1_hash(event_query)
        self.session.post(event_url, json={})

    def sendEvent(self, eventValue, payload=None):
        unix_time = str(int(time.time()))
        query = (
            f"?a={self.offerData.apiKey}&aifa={self.ad_id}&av=1.4.6&c=wifi"
            f"&event_index=15&i={self.offerData.packageName}&k=AIFA"
            f"&lag=0.07100000000000001&n={eventValue}&p=Android&rt=json"
            f"&s={unix_time}&sdk=Singular%2Fv12.5.5-Unity%2F4.4.1"
            f"&seq=5&singular_install_id={self.device_id}&t=407.844&u={self.ad_id}"
        )
        payload_data = None
        if payload:
            inner_payload = json.dumps(payload, separators=(',', ':'))
            escaped_payload = json.dumps({"e": inner_payload}, separators=(',', ':'))
            payload_data = {
                "payload": escaped_payload,
                "signature": self.sha1_hash(escaped_payload)
            }

        event_url = self.api + "event" + query + f"&h=" + self.sha1_hash(query)
        self.session.post(event_url, json=payload_data, verify=False)

    def sendLevel(self, i):
        self.sendEvent(
            f"mn_milestone_0{i}",
            {
                "e": {
                    "interstitial_views": i,
                    "rewarded_views": i,
                    "ltv": 0.00840899,
                    "time": (i * 50),
                    "is_revenue_event": False
                }
            }
        )
        time.sleep(15)