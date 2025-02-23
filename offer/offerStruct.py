from dataclasses import dataclass, asdict, field
import json
import string
import time
from typing import Any, Dict, List


@dataclass
class offerStruct:
    offerName: int = 0
    partnerName: string = "adjust"
    offerToken:string = ""
    offerEventTokens: List[str] = field(default_factory=list)
    tokenDelay: List[int]  = field(default_factory=list)
    milestones: List[int]  = field(default_factory=list)
    isDaily: bool = False
    dailyMaxTask: int = 0
    maxTask: int = 0
    secretKey: string = ""
    appLink: string = " "
    packageName: string = ""
    apiKey: string = ""

@dataclass
class DailyAdData:
    gameData :offerStruct
    dailyCap : int
    lifetimeCap : int
    currentCap : int
    nextDailyCap : int
    uuid : string
    processing : bool = False
    userId: string = ""
    
@dataclass
class offerData:
    offerData: offerStruct
    ad_id: str
    processing: bool = False
    completed: bool = False
    offerIndex: int = 0
    attributed: bool=False
    offerLastUpdate: int = 0
    def updateIndex(self,Index):
        self.offerIndex = Index
        self.offerLastUpdate = int(time.time())
    offerUUID: string = ""

@dataclass
class userStruct:
    user_name: str
    last_offer: int = 0
    total_offer_send: int = 0
    active_offer: List[offerData] = field(default_factory=list)
    
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DailyAdData):
            # Customize serialization for DailyAdData objects
            return {
                'gameData': obj.gameData,  # Assuming gameData is serializable
                'dailyCap': obj.dailyCap,
                'lifetimeCap': obj.lifetimeCap,
                'currentCap': obj.currentCap,
                'nextDailyCap': obj.nextDailyCap,
                'uuid': obj.uuid,
                'userId': obj.userId,
            }
        
        elif isinstance(obj, offerStruct):
            return {
                'offerName': obj.offerName,
                'offerToken': obj.offerToken,
                'gameEventTokens': obj.gameEventTokens,
                'tokenDelay': obj.tokenDelay,
                'isDaily': obj.isDaily
            }
        return super().default(obj)
    
