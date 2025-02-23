from dataclasses import dataclass, field, asdict, is_dataclass
from misc.misc import generate_unique_uuid
import time
from typing import Any, Dict, List
from offer.offers import offerStruct
from offer.offerStruct import offerData, userStruct,DailyAdData
import threading
import json
from atomicwrites import atomic_write

OFFER_LIMIT = 150

class UserManager:
    
    def __init__(self):
        self.users: List[userStruct] = [] 
        self.lock = threading.Lock()
        self.loadUsers()
        ##set all processing to false
        for user in self.users:
            for offer in user.active_offer:
                offer.processing = False
        threading.Thread(target=self.autoSave, args=()).start()
    
    def exportUsers(self):
        with self.lock:
            users_dict = [asdict(user) for user in self.users]
            with atomic_write('files/users.json', overwrite=True) as f:
                json.dump(users_dict, f, indent=4)
   
    def autoSave(self):
        while True:
            time.sleep(3)
            self.exportUsers()
   
    def loadUsers(self):
        with self.lock:
            try:
                with open('files/users.json', 'r') as f:
                    users_dict = json.load(f)
                    self.users = []
                    for user in users_dict:
                        active_offers = [offerData(
                            offerData=offerStruct(**offer['offerData']),
                            ad_id=offer['ad_id'],
                            processing=offer['processing'],
                            completed=offer['completed'],
                            offerUUID=offer['offerUUID'],
                            offerIndex=offer['offerIndex'],
                            attributed=offer['attributed'],
                            offerLastUpdate=offer['offerLastUpdate']
                        ) for offer in user['active_offer']]
                        user_obj = userStruct(
                            user_name=user['user_name'],
                            last_offer=user['last_offer'],
                            total_offer_send=user['total_offer_send'],
                            active_offer=active_offers
                        )
                        self.users.append(user_obj)
            except Exception as e:
                self.users = []
    
    def canSendOffer(self,name,without_add=False):
        with self.lock:
            for user in self.users:
                if user.user_name == name:
                    if user.last_offer == 0 or time.time() - user.last_offer   > 43200:
                        user.last_offer = int(time.time())
                        user.total_offer_send = 0
                    if OFFER_LIMIT > user.total_offer_send :
                        if not without_add:
                            user.total_offer_send += 1
                        return True
                    else:
                        return False
        if without_add:
            return True
        return False
                    
    def setOfferStatus(self,offerUUID,name,completed=None,processing=None,offerIndex=None,attributed=None):
        with self.lock:
            for user in self.users:
                if user.user_name == name:
                    for offer in user.active_offer:
                        if offerUUID == offer.offerUUID:
                            if completed != None:
                                offer.completed = completed
                            if processing != None:
                                offer.processing = processing
                            if offerIndex != None:
                                offer.updateIndex(offerIndex)
                            if attributed != None:
                                offer.attributed = attributed
                                offer.offerLastUpdate = int(time.time())
                            return offer
    
    def removeOffer(self,name,offerUUID):
        with self.lock:
            for user in self.users:
                if user.user_name == name:
                    for offer in user.active_offer:
                        if offerUUID == offer.offerUUID:
                            user.active_offer.remove(offer)
                            return
    
    def addOffer(self, name, ad_id, offer: offerStruct,proccessing=False):
        offerUUID= generate_unique_uuid()
        with self.lock:
            for user in self.users:
                if user.user_name == name:
                    for active_offer in user.active_offer:
                        if active_offer.ad_id == ad_id and active_offer.offerData.offerName == offer.offerName:
                            return active_offer.offerUUID
                    user.active_offer.append(offerData(offerData=offer, ad_id=ad_id,processing=proccessing,offerUUID=offerUUID))
                    return offerUUID
            new_user = userStruct(user_name=name)
            new_user.active_offer.append(offerData(offerData=offer, ad_id=ad_id,processing=proccessing,offerUUID=offerUUID))
            self.users.append(new_user)
            return offerUUID
   
    def getOffer(self,name,offerUUID) -> offerData:
        with self.lock:
            for user in self.users:
                if user.user_name == name:
                    for offer in user.active_offer:
                        if offer.offerUUID == offerUUID:
                            return offer
        return None
    
    def getFreeOffer(self):
        with self.lock:
            for user in self.users:
                for offer in user.active_offer:
                    if not offer.completed and offer.processing == False and OFFER_LIMIT > user.total_offer_send and len(offer.offerData.milestones) > offer.offerIndex  :
                        return user.user_name,offer
            return None,None
   
    def getFreeOffers(self):
        totalOffers = {}
        with self.lock:
            for user in self.users:
                totalOffers[user.user_name] = []
                for offer in user.active_offer:
                    offerCount = len(offer.offerData.offerEventTokens) if offer.offerData.partnerName == "adjust" else len(offer.offerData.milestones)
                    if not offer.completed and offer.processing == False and OFFER_LIMIT > user.total_offer_send and offerCount >= offer.offerIndex :
                        totalOffers[user.user_name].append(offer)
        return totalOffers

    def decreaseOfferCount(self, name):
        with self.lock:
            for user in self.users:
                if user.user_name == name:
                    if user.total_offer_send > 0:
                        user.total_offer_send -= 1
                    return

userManager = UserManager()