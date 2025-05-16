import logging
from datetime import datetime, timezone
import botocore.exceptions as ClientError
from colorama import Fore, init

init(autoreset=True)

def clean_unused_elbs(session, region, delete=False):
    elb_client = session.client("elb", region_name=region)
    deleted_count = 0

    try:
        elbs = elb_client.describe_load_balancers().get("LoadBalancerDescriptions", [])
        for elb in elbs:
            elb_name = elb["LoadBalancerName"]
            instance_ids = elb.get("Instances", [])
            if not instance_ids:
                logging.info(f"{Fore.CYAN}🧯 Found unused ELB: {elb_name}")
                deleted_count += 1
                if delete:
                    try:
                        elb_client.delete_load_balancer(LoadBalancerName=elb_name)
                        logging.warning(f"{Fore.YELLOW}🟡 Deleted unused ELB: {elb_name}")
                    except ClientError as e:
                        logging.error(f"{Fore.RED}❌ Failed to delete ELB {elb_name}: {e}")
                else:
                    logging.info(f"{Fore.MAGENTA}🧪 [DRY-RUN] Would delete ELB: {elb_name}")

    except ClientError as e:
        logging.error(f"{Fore.RED}❌ Error retrieving ELBs in {region}: {e}")

    if delete:
        logging.info(f"{Fore.GREEN}✅ Finished processing {region}. {deleted_count} unused ELBs deleted.")
    else:
        logging.info(f"{Fore.BLUE}🧪 Dry-run complete for {region}. {deleted_count} unused ELBs identified.")

    return deleted_count
