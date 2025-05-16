import logging
from datetime import datetime, timezone
import botocore.exceptions as ClientError
from colorama import Fore, init

init(autoreset=True)

def clean_unattached_volumes(session, region, delete=False):
    ec2_client = session.client("ec2", region_name=region)
    unattached_volume_count = 0

    try:
        pagination = ec2_client.get_paginator('describe_volumes').paginate(
            Filters=[
                {
                    'Name': 'status',
                    'Values': ['available']
                }
            ]
        )

        for page in pagination:
            for volume in page["Volumes"]:
                volume_id = volume["VolumeId"]
                size = volume["Size"]
                created_time = volume["CreateTime"]
                age = datetime.now(timezone.utc) - created_time

                logging.info(
                    f"{Fore.CYAN}📦 Unattached volume: {volume_id} | Size: {size} GiB | Age: {age.days} days"
                )

                unattached_volume_count += 1

                if delete:
                    try:
                        ec2_client.delete_volume(VolumeId=volume_id)
                        logging.warning(f"{Fore.YELLOW}🟡 Deleted volume: {volume_id}")
                    except ClientError as e:
                        logging.error(f"{Fore.RED}❌ Failed to delete {volume_id}: {e}")
                else:
                    logging.info(f"{Fore.MAGENTA}🧪 [DRY-RUN] Would delete: {volume_id}")

    except ClientError as e:
        logging.error(f"{Fore.RED}❌ Error describing volumes in {region}: {e}")

    if delete:
        logging.info(
            f"{Fore.GREEN}✅ Cleanup completed for {region}. {unattached_volume_count} volumes processed and deleted."
        )
    else:
        logging.info(
            f"{Fore.BLUE}🧪 Dry-run complete for {region}. {unattached_volume_count} volumes identified for deletion."
        )

    return unattached_volume_count