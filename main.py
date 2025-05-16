import argparse
import logging

from cleaner import ec2_cleaner, ebs_cleaner, eip_cleaner, elb_cleaner
from utils.aws_client import init_boto3_session
from utils.logger import setup_logger


def parse_args():
    parser = argparse.ArgumentParser(description="AWS Resource Cleaner")
    parser.add_argument(
        "--profile", type=str, default="default", help="AWS CLI profile to use"
    )
    parser.add_argument(
        "--region", type=str, default="us-east-1", help="AWS region to target"
    )
    parser.add_argument(
        "--delete", action="store_true", help="Actually delete resources instead of dry-run"
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO", help="Set logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    return parser.parse_args()

def main():
    args = parse_args()    
    # print(args)
    # python3 main.py --profile personal --region ap-south-1
    # Namespace(profile='personal', region='ap-south-1', delete=False, log_level='INFO')

    setup_logger(args.log_level)

    # Initialize AWS session
    session = init_boto3_session(args.profile, args.region)

    logging.info("🔍 Starting AWS Resource Cleaner (Dry Run: %s)", not args.delete)

    # Run EC2 cleanup
    ec2_cleaner.clean_stopped_instances(session, args.region, args.delete)
    
    ebs_cleaner.clean_unattached_volumes(session, args.region, args.delete)

    eip_cleaner.clean_unassociated_eips(session, args.region, args.delete)

    elb_cleaner.clean_unused_elbs(session, args.region, args.delete)

    logging.info("✅ Cleanup completed.")


if __name__ == "__main__":
    main()
