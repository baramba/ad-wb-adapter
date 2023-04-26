from exceptions.base import WBACampaignError


class CampaignCreateError(WBACampaignError):
    pass


class CampaignInitError(WBACampaignError):
    pass


class CampaignStartError(WBACampaignError):
    pass
