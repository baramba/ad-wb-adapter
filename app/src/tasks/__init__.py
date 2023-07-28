from tasks.create_full_campaign import CampaignCreateFullTask as ccft
from tasks.restart_create_campaign import СontinueCreateCampaignTask as ccct

tasks = [
    ccft.create_full_campaign,
    ccct.continue_create_campaign
    # CampaignTasks.create_campaign,
    # CampaignTasks.add_keywords_to_campaign,
    # CampaignTasks.replenish_budget,
    # CampaignTasks.start_campaign,
    # CampaignTasks.switch_on_fixed_list,
]
