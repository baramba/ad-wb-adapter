class CampaignError(Exception):
    status_code: int

    @classmethod
    def init(cls, status_code: int, message: str):
        result = cls(message)
        result.status_code = status_code
        return result


class CampaignCreateError(CampaignError):
    pass


class CampaignInitError(CampaignError):
    pass


class CampaignStartError(CampaignError):
    pass
