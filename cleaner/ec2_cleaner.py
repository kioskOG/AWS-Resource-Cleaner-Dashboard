# # cleaner/ec2_cleaner.py
# import logging
# from datetime import datetime, timezone, timedelta
# from colorama import Fore, init

# init(autoreset=True)

# def clean_stopped_instances(session, region, delete=False):
#     ec2 = session.client('ec2', region_name=region)
#     response = ec2.describe_instances(
#         Filters=[
#             {'Name': 'instance-state-name', 'Values': ['stopped']}
#         ]
#     )

#     stopped_instances = []
#     for reservation in response['Reservations']:
#         for instance in reservation['Instances']:
#             instance_id = instance['InstanceId']
#             launch_time = instance['LaunchTime']
#             uptime = datetime.now(timezone.utc) - launch_time
#             stopped_instances.append(instance_id)
#             logging.info(f"{Fore.CYAN}🖥️ Found stopped EC2 instance: {instance_id} | Uptime: {uptime.days} days")

#     if not stopped_instances:
#         logging.info(f"{Fore.BLUE}📭 No stopped EC2 instances found in {region}.")
#         return 0

#     if delete:
#         try:
#             ec2.terminate_instances(InstanceIds=stopped_instances)
#             logging.warning(f"{Fore.YELLOW}🟡 Terminated EC2 instances: {', '.join(stopped_instances)}")
#         except Exception as e:
#             logging.error(f"{Fore.RED}❌ Error terminating instances: {e}")
#     else:
#         logging.info(f"{Fore.MAGENTA}🧪 [DRY-RUN] Would terminate EC2 instances: {', '.join(stopped_instances)}")
    
#     return len(stopped_instances)


# cleaner/ec2_cleaner.py
import logging
from datetime import datetime, timezone, timedelta
from colorama import Fore, init

init(autoreset=True)

def clean_stopped_instances(session, region, delete=False, idle_days=1):
    ec2 = session.client('ec2', region_name=region)
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['stopped']}
        ]
    )

    terminatable_instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            if 'StateTransitionReason' in instance:
                reason = instance['StateTransitionReason']
                if reason.startswith("User initiated shutdown") or reason.startswith("Client.UserInitiatedShutdown"):
                    if 'StopTime' in instance:
                        stop_time = instance['StopTime']
                        idle_duration = datetime.now(timezone.utc) - stop_time
                        if idle_duration > timedelta(days=idle_days):
                            terminatable_instances.append(instance_id)
                            logging.info(f"{Fore.CYAN}🛑 Found stopped EC2 instance (idle > {idle_days} day(s)): {instance_id} | Stopped Since: {stop_time.strftime('%Y-%m-%d %H:%M:%S UTC')} | Idle Time: {idle_duration.days} days")
                    else:
                        logging.warning(f"{Fore.YELLOW}⚠️ Found stopped EC2 instance {instance_id} without StopTime information. Skipping idle check.")
                else:
                    logging.info(f"{Fore.BLUE}ℹ️ Stopped EC2 instance {instance_id} stopped for reason: '{reason}'. Skipping idle check.")
            else:
                logging.warning(f"{Fore.YELLOW}⚠️ Found stopped EC2 instance {instance_id} without StateTransitionReason. Skipping idle check.")

    if not terminatable_instances:
        logging.info(f"{Fore.BLUE}📭 No stopped EC2 instances idle for more than {idle_days} day(s) found in {region}.")
        return 0

    if delete:
        try:
            ec2.terminate_instances(InstanceIds=terminatable_instances)
            logging.warning(f"{Fore.YELLOW}🟡 Terminated EC2 instances (idle > {idle_days} day(s)): {', '.join(terminatable_instances)}")
        except Exception as e:
            logging.error(f"{Fore.RED}❌ Error terminating instances: {e}")
    else:
        logging.info(f"{Fore.MAGENTA}🧪 [DRY-RUN] Would terminate EC2 instances (idle > {idle_days} day(s)): {', '.join(terminatable_instances)}")

    return len(terminatable_instances)
