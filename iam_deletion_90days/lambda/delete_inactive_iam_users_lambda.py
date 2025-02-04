import boto3
import datetime
import os

# AWS Organizations client
org_client = boto3.client("organizations")

# Email settings (Update these values)
SES_REGION = os.getenv("SES_REGION", "us-east-1")  # Change if needed
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "noreply@yourcompany.com") #change to our SES handler

# Number of days for warnings and deletions
WARNING_DAYS = 60
DELETION_DAYS = 90

# Role to assume in each account
ROLE_NAME = "OrganizationAccountAccessRole"

def assume_role(account_id):
    """Assumes a role in the target AWS account and returns a session."""
    sts_client = boto3.client("sts")
    role_arn = f"arn:aws:iam::{account_id}:role/{ROLE_NAME}"
    
    try:
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="IAMUserCleanup"
        )
        credentials = response["Credentials"]
        return boto3.client(
            "iam",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"]
        )
    except Exception as e:
        print(f"[ERROR] Failed to assume role for account {account_id}: {str(e)}")
        return None

def send_email(user_email, username, days_inactive):
    """Sends a warning email to the user via AWS SES."""
    ses_client = boto3.client("ses", region_name=SES_REGION)

    subject = f"Inactive AWS Account - Action Required for {username}"
    body = f"""
    Hello {username},

    Your AWS IAM account has been inactive for {days_inactive} days.
    Per company security policy, inactive accounts will be deleted after {DELETION_DAYS} days of inactivity.

    If you need to retain access, please log into AWS as soon as possible.
    If no action is taken, your account will be permanently deleted.

    Best,
    Security Team
    """

    try:
        ses_client.send_email(
            Source=EMAIL_SENDER,
            Destination={"ToAddresses": [user_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}}
            }
        )
        print(f"[INFO] Warning email sent to {user_email} for user {username}")
    except Exception as e:
        print(f"[ERROR] Failed to send email to {user_email}: {str(e)}")

def process_iam_users(account_id):
    """Processes inactive IAM users in the given AWS account."""
    iam_client = assume_role(account_id)
    if not iam_client:
        return

    try:
        users = iam_client.list_users()["Users"]
        now = datetime.datetime.utcnow()

        for user in users:
            username = user["UserName"]
            last_used = iam_client.get_user(UserName=username)["User"].get("PasswordLastUsed")

            if not last_used:
                print(f"[INFO] User {username} has never logged in. Skipping...")
                continue

            last_used = last_used.replace(tzinfo=None)
            days_inactive = (now - last_used).days

            if days_inactive >= WARNING_DAYS and days_inactive < DELETION_DAYS:
                # Retrieve user email (Assuming it is stored in IAM tags)
                tags = iam_client.list_user_tags(UserName=username).get("Tags", [])
                email = next((tag["Value"] for tag in tags if tag["Key"] == "email"), None)

                if email:
                    send_email(email, username, days_inactive)
                else:
                    print(f"[WARNING] No email found for user {username}, cannot send warning.")

            elif days_inactive >= DELETION_DAYS:
                print(f"[INFO] Deleting user {username} due to {days_inactive} days of inactivity.")
                try:
                    iam_client.delete_login_profile(UserName=username)
                    attached_policies = iam_client.list_attached_user_policies(UserName=username)["AttachedPolicies"]
                    for policy in attached_policies:
                        iam_client.detach_user_policy(UserName=username, PolicyArn=policy["PolicyArn"])

                    access_keys = iam_client.list_access_keys(UserName=username)["AccessKeyMetadata"]
                    for key in access_keys:
                        iam_client.delete_access_key(UserName=username, AccessKeyId=key["AccessKeyId"])

                    iam_client.delete_user(UserName=username)
                    print(f"[SUCCESS] User {username} deleted.")

                except Exception as e:
                    print(f"[ERROR] Failed to delete user {username}: {str(e)}")

    except Exception as e:
        print(f"[ERROR] Failed to process users in account {account_id}: {str(e)}")

def list_accounts():
    """Retrieves a list of all AWS accounts in the organization."""
    accounts = []
    try:
        paginator = org_client.get_paginator("list_accounts")
        for page in paginator.paginate():
            accounts.extend(page["Accounts"])
    except Exception as e:
        print(f"[ERROR] Failed to list AWS accounts: {str(e)}")
    return accounts

def lambda_handler(event, context):
    """AWS Lambda entry point."""
    accounts = list_accounts()
    for account in accounts:
        account_id = account["Id"]
        account_name = account["Name"]

        print(f"\n[INFO] Processing IAM users in account: {account_name} ({account_id})")
        process_iam_users(account_id)

    return {"status": "Completed IAM user cleanup"}
