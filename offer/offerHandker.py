from dataclasses import dataclass
from enum import Enum
import time
from typing import Optional
from offer.offerStruct import offerStruct,offerData
from singular.singular import SingularApi
from adjust.adjust import AdjustApi
from offer.offerCache import userManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('OfferHandler')

class PartnerType(Enum):
    SINGULAR = "singular"
    ADJUST = "adjust"
    
@dataclass
class OfferStatus:
    processing: bool = False
    completed: bool = False
    offer_index: Optional[int] = None
    attributed: Optional[bool] = None

class OfferHandler:
    def __init__(self, ad_id: str, proxy: str, name: str, offer_data: offerStruct):
        self.offer = offer_data
        self.ad_id = ad_id
        self.proxy = proxy
        self.name = name
        self.can_handle = userManager.canSendOffer(name, without_add=True)
        self.offer_uuid = userManager.addOffer(name, ad_id, offer_data, self.can_handle)
        self.offer_data = userManager.getOffer(name, self.offer_uuid)
        logger.info(f"Initializing OfferHandler for user {name} with ad_id {ad_id}")
        if self.offer_data.offerIndex == -1:
            self.offer_data.offerIndex = 0
        
    def _update_offer_status(self, status: OfferStatus) -> None:
        self.offer_data = userManager.setOfferStatus(
            name=self.name,
            processing=status.processing,
            completed=status.completed,
            offerIndex=status.offer_index,
            offerUUID=self.offer_uuid,
            attributed=status.attributed,
        )

    def _handle_singular_offer(self, api: SingularApi) -> None:
        logger.info(f"Starting Singular offer handling for user {self.name}")
        api.createSession()
        
        if not self.offer_data.attributed:
            logger.info("Waiting 6 minutes for attribution")
            time.sleep(360)
            self._update_offer_status(OfferStatus(attributed=True))

        if self.offer.milestones:
            logger.info("Processing milestone-based offer")
            self._process_milestones(api)
        else:
            logger.info("Processing regular offer tokens")
            self._process_offer_tokens(api)

    def _process_milestones(self, api: SingularApi) -> None:
        total_milestones = len(self.offer.milestones)
        logger.info(f"Processing {total_milestones} milestones, starting from index {self.offer_data.offerIndex}")

        for index in range(self.offer_data.offerIndex, total_milestones):
            token = self.offer.milestones[index]
            if not userManager.canSendOffer(self.name):
                self._update_offer_status(OfferStatus(processing=False))
                logger.warning(f"Cannot send offer for user {self.name}, stopping milestone processing")
                break

            api.sendLevel(token)
            self._update_offer_status(OfferStatus(
                offer_index=index+1,
                completed=token == self.offer.milestones[-1],
                processing=token != self.offer.milestones[-1]
            ))
            time.sleep(15)
  
    def _process_offer_tokens(self, api: SingularApi) -> None:
        for token in self.offer.offerToken:
            if not userManager.canSendOffer(self.name):
                self._update_offer_status(OfferStatus(processing=False))
                break

            api.sendEvent(token)
            time.sleep(15)

            if token == self.offer.offerToken[-1]:
                self._update_offer_status(OfferStatus(processing=False, completed=True))

    def _handle_adjust_offer(self, api: AdjustApi) -> None:
        api.createSession()
        time.sleep(5)
        
        if not (self.offer_data.attributed or api.attribution()):
            userManager.removeOffer(self.name, self.offer_uuid)
            return

        if not self.offer_data.attributed:
            self._update_offer_status(OfferStatus(attributed=True))
            time.sleep(30)

        if self.offer.isDaily:
            self._process_daily_tasks(api)
        else:
            self._process_event_tokens(api)

    def _process_daily_tasks(self, api: AdjustApi) -> None:
        for i in range(self.offer.dailyMaxTask):
            if not userManager.canSendOffer(self.name):
                self._update_offer_status(OfferStatus(processing=False))
                break

            time.sleep(self.offer.tokenDelay[0])
            api.sendEvent(self.offer.offerEventTokens[0])

            if i == self.offer.dailyMaxTask - 1:
                self._update_offer_status(OfferStatus(processing=False, completed=True))

    def _process_event_tokens(self, api: AdjustApi) -> None:
        for index in range(self.offer_data.offerIndex, len(self.offer.offerEventTokens)):
            token = self.offer.offerEventTokens[index]

            if not userManager.canSendOffer(self.name, True):
                self._update_offer_status(OfferStatus(processing=False))
                break

            sleep_time = self._calculate_sleep_time(index)
            if sleep_time > 0:
                time.sleep(sleep_time)

            if userManager.canSendOffer(self.name):
                if not api.sendEvent(token):
                    userManager.decreaseOfferCount(self.name)
                
                self._update_offer_status(OfferStatus(
                    offer_index=index+1,
                    processing=index != len(self.offer.offerEventTokens) - 1,
                    completed=index == len(self.offer.offerEventTokens) - 1
                ))

    def _calculate_sleep_time(self, index: int) -> int:
        last_task_seconds = time.time() - self.offer_data.offerLastUpdate
        return max(0, int(self.offer.tokenDelay[index] - last_task_seconds))

    def handleTask(self) -> None:
        if not self.can_handle:
            return

        self._update_offer_status(OfferStatus(processing=True))

        if self.offer.partnerName == PartnerType.SINGULAR.value:
            api = SingularApi(self.ad_id, self.proxy, self.offer)
            self._handle_singular_offer(api)
        elif self.offer.partnerName == PartnerType.ADJUST.value:
            api = AdjustApi(self.ad_id, self.proxy, self.offer)
            self._handle_adjust_offer(api)