#-* -coding:utf-8 -*-
from capsules.authorization.models.claim import CapsuleClaimModel


class CapsulePrivacyService:
    def __init__(self):
        pass

    async def get_capsules_by_claim(self, claim: CapsuleClaimModel):
        """
        Get capsules by claim
        """
        pass

capsule_privacy_srv = CapsulePrivacyService()