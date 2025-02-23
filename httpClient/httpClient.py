import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

class httpClient:
    def __init__(self, retries=5, backoff_factor=0.3, status_forcelist=None,
               user_agent=None, proxy_str=None):
        if status_forcelist is None:
            status_forcelist = [500, 502, 503, 504]

        self.session = requests.Session()
        retries = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=None
        )
        
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.verify = False
        self.session.headers = {
            "accept-encoding": "gzip"
        }
        
        if user_agent:
            self.session.headers.update({"User-Agent": user_agent})
            
        if proxy_str:
            proxy_host = proxy_str.split(':')[0] + ':' + proxy_str.split(':')[1]
            username = proxy_str.split(':')[2]
            password = proxy_str.split(':')[3]
            proxy = f"http://{username}:{password}@{proxy_host}"
            self.session.proxies = {
                "http": proxy,
                "https": proxy
            }

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.session.post(url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.session.put(url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.session.delete(url, **kwargs)

    def request(self, method, url, **kwargs):
        return self.session.request(method=method.upper(), url=url, **kwargs)
    
    def __getattr__(self, item):
        return getattr(self.session, item)