class CampaignError(Exception):
    pass

    def __init__(self, status_code: int, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.status_code = status_code


class CampaignCreateError(CampaignError):
    pass


class CampaignInitError(CampaignError):
    pass


class CampaignStartError(CampaignError):
    pass
