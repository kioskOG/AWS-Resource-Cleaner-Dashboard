# 🧹 AWS Resource Cleaner Dashboard

A **Streamlit-based web interface** to safely scan and clean up unused AWS resources like:

* 🖥️ Stopped EC2 Instances
* 📦 Unattached EBS Volumes
* 🌐 Unassociated Elastic IPs (EIPs)
* 🧱 Unused Elastic Load Balancers (ELBs)

Built on top of a modular CLI tool (`main.py`), this dashboard helps visualize and control AWS resource cleanup operations interactively.

---

## 🚀 Features

* 🔍 **Scan Mode**: Preview resources across regions without making changes
* 🗑️ **Delete Mode**: Actually terminate/delete selected resource types
* ✅ **Deletion Confirmation**: Checkbox required before destructive actions
* 🎛️ **Selective Cleanup**: Enable/disable EC2, EBS, EIP, ELB independently
* 🧾 **Real-Time Logs**: Live output of actions taken (or to be taken)
* 🌍 **Dynamic Region Picker**: Lists AWS regions for chosen profile
* 🔐 **Profile-Based Access**: Works with any configured AWS CLI profile

---

# 🧱 Project Structure

```bash
aws-resource-cleaner/
├── cleaner/
│   ├── __init__.py
│   ├── ec2_cleaner.py
│   ├── ebs_cleaner.py
│   ├── eip_cleaner.py
│   ├── elb_cleaner.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── aws_client.py
├── main.py
├── requirements.txt
├── README.md
```

---

## 🛠️ Setup & Run

### 📦 Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate ## for mac & linux
pip install -r requirements.txt
```

### 🧪 Verify AWS CLI configuration

Make sure your AWS credentials are properly set up via:

```bash
aws configure --profile your-profile-name
```

## 🧰 CLI Design (via argparse)

```bash
# Dry-run mode (default)
python3 main.py --profile default --region us-east-1

# Actually delete unused resources
python3 main.py --delete --profile default --region us-east-1
```

>[!NOTE]
> If you wanna access this in UI, use the below option

## UI based

```bash
streamlit run dashboard.py
```

> [!IMPORTANT]
> update the value of `AWS Profile` in dashboard.py to your respective `AWS Profile` like **default**.

## CLI Options

| Option        | Description                                   |
| ------------- | --------------------------------------------- |
| `--delete`    | Flag to actually delete resources             |
| `--profile`   | AWS profile to use (default is `default`)     |
| `--region`    | Region to operate in (default is `us-east-1`) |
| `--log-level` | Logging level (default is `INFO`)             |

## ✅ Resources to Clean

| Resource       | Criteria                     |
| -------------- | ---------------------------- |
| EC2 Instances  | `Uptime`: `No. of days` days        |
| EBS Volumes    | `available` (not attached)   |
| Elastic IPs    | Not associated with instance |
| ELBs (Classic) | No associated instances      |


## 🪵 Logging Sample (INFO level)

```bash
[2025-05-15 13:21:33,228] [INFO] [🔍 Starting AWS Resource Cleaner (Dry Run: True)]
[2025-05-15 13:21:33,236] [INFO] [Found credentials in shared credentials file: ~/.aws/credentials]
[2025-05-15 13:21:33,641] [INFO] [🖥️ Found stopped EC2 instance: i-037b655f6228cf8c1 | Uptime: 0 days]
[2025-05-15 13:21:33,641] [INFO] [🧪 [DRY-RUN] Would terminate EC2 instances: i-037b655f6228cf8c1]
[2025-05-15 13:21:33,968] [INFO] [🧪 Dry-run complete for ap-south-1. 0 volumes identified for deletion.]
[2025-05-15 13:21:34,211] [INFO] [🧪 Dry-run complete. 0 unassociated EIPs found.]
[2025-05-15 13:21:34,214] [INFO] [✅ Cleanup completed.]
```

## Color Output

✅ outputs colorized logs using colorama, improving readability:

🟦 Info messages are cyan/blue
🟨 Warnings are yellow/magenta
🟥 Errors are red
✅ Summary messages show in green/blue

---

## 📄 License

MIT © Jatin Sharma
