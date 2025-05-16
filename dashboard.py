import streamlit as st
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError, ClientError, ProfileNotFound
from cleaner import ec2_cleaner, ebs_cleaner, eip_cleaner, elb_cleaner
import logging
from utils.aws_client import init_boto3_session


logger = logging.getLogger(name="streamlit")
if not logger.hasHandlers():
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

st.set_page_config(page_title="AWS Resource Cleaner", layout="wide")
st.title("🧹 AWS Resource Cleaner Dashboard")

profile = st.text_input("AWS Profile", value="personal")

# Dynamically get all available regions
regions = []
if profile:
    try:
        session = boto3.Session(profile_name=profile)
        ec2_client = session.client("ec2")
        all_regions = ec2_client.describe_regions()["Regions"]
        region_names = sorted([r["RegionName"] for r in all_regions])
    except (ProfileNotFound, NoCredentialsError, ClientError) as e:
        st.warning(f"⚠️ Failed to fetch regions: {e}")
        region_names = ["us-east-1", "us-west-2", "ap-south-1"]

if region_names:
    region = st.selectbox("AWS Region", region_names)
else:
    region = st.selectbox("AWS Region (fallback)", ["us-east-1", "us-west-2", "ap-south-1"])

delete_flag = st.checkbox("⚠️ Actually Delete Resources", value=False)

# Individual resource toggles
st.markdown("### 🧩 Select Resources to Process")
run_ec2 = st.checkbox("🖥️ EC2 Instances", value=True)
run_ebs = st.checkbox("📦 EBS Volumes", value=True)
run_eip = st.checkbox("🌐 Elastic IPs", value=True)
run_elb = st.checkbox("🧱 Load Balancers", value=True)


log_output = st.empty()
log_lines = []


def log(message, level="info"):
    log_lines.append(message)
    if level == "info":
        logger.info(message)
    elif level == "warn":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    log_output.text("\n".join(log_lines))

# Dynamic button label
button_label = "🗑️ Delete Selected Resources" if delete_flag else "🔍 Scan Selected Resources"

# Simulate confirmation before deletion
confirm_delete = True
if delete_flag:
    confirm_delete = st.checkbox("✅ Yes, I confirm resource deletion.")

if st.button(button_label):
    if delete_flag and not confirm_delete:
        st.warning("⚠️ Please confirm deletion to proceed.")
    else:
        try:
            session = init_boto3_session(profile, region)
            log(f"✅ Initialized session for profile '{profile}' in region '{region}'")

            if run_ec2:
                ec2_count = ec2_cleaner.clean_stopped_instances(session, region, delete=delete_flag)
                log(f"🖥️ EC2 stopped instances found: {ec2_count or 0}")

            if run_ebs:
                ebs_count = ebs_cleaner.clean_unattached_volumes(session, region, delete=delete_flag)
                log(f"📦 EBS unattached volumes found: {ebs_count or 0}")

            if run_eip:
                eip_count = eip_cleaner.clean_unassociated_eips(session, region, delete=delete_flag)
                log(f"🌐 EIP unassociated addresses found: {eip_count or 0}")

            if run_elb:
                elb_count = elb_cleaner.clean_unused_elbs(session, region, delete=delete_flag)
                log(f"🧱 Unused ELBs found: {elb_count or 0}")

            st.success("✅ Cleanup completed." if delete_flag else "✅ Scan complete.")

        except (NoCredentialsError, BotoCoreError, ClientError) as e:
            log(f"❌ AWS Error: {e}", level="error")
            st.error("AWS session or permission issue.")
        except Exception as e:
            log(f"❌ Unexpected error: {e}", level="error")
            st.error("Unexpected error occurred. Check logs.")

