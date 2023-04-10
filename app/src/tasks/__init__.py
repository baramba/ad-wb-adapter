import tasks.create_full_campaign as cfm
from tasks.campaign_tasks import CampaignTasks

tasks = [
    cfm.create_full_campaign,
    CampaignTasks.create_campaign,
    CampaignTasks.add_keywords_to_campaign,
    CampaignTasks.replenish_budget,
    CampaignTasks.start_campaign,
    CampaignTasks.switch_on_fixed_list,
]
