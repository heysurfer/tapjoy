import json
import random
import time
import concurrent.futures
import logger
import threading
import logging
from tapjoy.tapjoy import TapjoyManager
from offer.offerHandker import OfferHandler
from offer.offerCache import userManager
logger.logger.setLevel(logging.DEBUG)

random.seed(time.time())


PROXY_URL = f""

def handle_tapjoy(name: str, eid: str) -> None:
    try:
        proxy_url = PROXY_URL

        manager = TapjoyManager(proxy_url, eid)
        offers = manager.getOffers()

        with open("files/response.html", "w", encoding="utf-8") as f:
            f.write(manager.html_content)

        threads = []
        for offer in offers:
            handler = OfferHandler(manager.ad_id, manager.proxy_str, name, offer)
            thread = threading.Thread(target=handler.handleTask)
            thread.start()
            threads.append(thread)



    except Exception as e:
        logging.error(f"Error processing Tapjoy offers for {name}: {str(e)}")

def start_eid() -> None:
    try:
        with open("files/eid.json", "r") as f:
            user_ids = json.load(f)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(handle_tapjoy, name, eid)
                for name, eids in user_ids.items()
                for eid in eids
            ]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Thread execution failed: {str(e)}")

    except json.JSONDecodeError as e:
        logging.error(f"Error reading eid.json: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in start_eid: {str(e)}")
        
def start_added_task():
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        cached_offers = userManager.getFreeOffers()
        for name, offers in cached_offers.items():
            for offer in offers:
                from offer.offers import get_offer_by_name
                offer_data = get_offer_by_name(offer.offerData.offerName)
                if offer_data:
                    handler = OfferHandler(offer.ad_id, "", name, offer_data)
                    futures.append(executor.submit(handler.handleTask))
                    time.sleep(3)
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Thread execution failed: {str(e)}")