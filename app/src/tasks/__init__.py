import tasks.create_full_campaign as cfm

tasks = [
    cfm.create_full_campaign,
    *cfm.private_tasks,

]
