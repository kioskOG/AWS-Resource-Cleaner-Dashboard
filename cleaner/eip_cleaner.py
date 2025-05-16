import botocore.exceptions as ClientError
import logging
from colorama import Fore, Style, init

init(autoreset=True)

def clean_unassociated_eips(session, region, delete=False):
    ec2_client = session.client("ec2", region_name=region)

    unassociated_eip_count = 0

    try:
        response = ec2_client.describe_addresses()
        addresses= response.get("Addresses", [])
        
        # or    addresses = ec2_client.describe_addresses()["Addresses"]

        for addr in addresses:
            if "AllocationId" not in addr:
                continue  # Skip addresses that can't be released
            if "InstanceId" not in addr and "NetworkInterfaceId" not in addr:
                unassociated_eip_count += 1
                public_ip = addr["PublicIp"]
                allocation_id = addr["AllocationId"]
                domain = addr.get("Domain", "unknown")

                logging.info(
                    f"{Fore.CYAN}🌐 Found unassociated EIP: {public_ip}, Allocation ID: {allocation_id}, Domain: {domain}"
                )

                if delete and allocation_id:
                    try:
                        ec2_client.release_address(AllocationId=allocation_id)
                        logging.warning(
                            f"{Fore.YELLOW}🟡 Released unassociated EIP: {public_ip} (Allocation ID: {allocation_id})"
                        )
                    except ClientError as e:
                        logging.error(
                            f"{Fore.RED}❌ Error releasing EIP {public_ip} (Allocation ID: {allocation_id}): {e}"
                        )
                elif delete and domain == "standard":
                    logging.warning(
                        f"{Fore.MAGENTA}⚠️ Cannot release standard EIP: {public_ip}. Requires disassociation first (if associated)."
                    )
    except ClientError as e:
        logging.error(f"{Fore.RED}❌ Error describing Elastic IP addresses in {region}: {e}")

    if delete:
        logging.info(
            f"{Fore.GREEN}✅ Finished processing {region}. {unassociated_eip_count} unassociated EIPs found and release attempted."
        )
    else:
        logging.info(
            f"{Fore.BLUE}🧪 Dry-run complete. {unassociated_eip_count} unassociated EIPs found."
        )
    return unassociated_eip_count
