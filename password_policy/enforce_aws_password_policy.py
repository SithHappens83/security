import boto3

# AWS Organizations client
org_client = boto3.client("organizations")

# Role to assume in each account
ROLE_NAME = "OrganizationAccountAccessRole"

# Password policy settings
PASSWORD_POLICY = {
    "MinimumPasswordLength": 8,
    "RequireSymbols": True,
    "RequireNumbers": True,
    "RequireUppercaseCharacters": True,
    "RequireLowercaseCharacters": True,
    "AllowUsersToChangePassword": True,
    "MaxPasswordAge": 90,  # Default 90 days unless MFA is enforced
    "PasswordReusePrevention": 12,
    "HardExpiry": False,  # Users are warned before expiry
}

def assume_role(account_id):
    """Assumes a role in the target AWS account and returns a session."""
    sts_client = boto3.client("sts")
    role_arn = f"arn:aws:iam::{account_id}:role/{ROLE_NAME}"
    
    try:
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="PasswordPolicyUpdate"
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

def enforce_password_policy(iam_client):
    """Enforces the password policy in the given AWS account."""
    try:
        iam_client.update_account_password_policy(
            MinimumPasswordLength=PASSWORD_POLICY["MinimumPasswordLength"],
            RequireSymbols=PASSWORD_POLICY["RequireSymbols"],
            RequireNumbers=PASSWORD_POLICY["RequireNumbers"],
            RequireUppercaseCharacters=PASSWORD_POLICY["RequireUppercaseCharacters"],
            RequireLowercaseCharacters=PASSWORD_POLICY["RequireLowercaseCharacters"],
            AllowUsersToChangePassword=PASSWORD_POLICY["AllowUsersToChangePassword"],
            MaxPasswordAge=PASSWORD_POLICY["MaxPasswordAge"],
            PasswordReusePrevention=PASSWORD_POLICY["PasswordReusePrevention"],
            HardExpiry=PASSWORD_POLICY["HardExpiry"]
        )
        print("[SUCCESS] Password policy updated successfully")
    except Exception as e:
        print(f"[ERROR] Failed to update password policy: {str(e)}")

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

def main():
    """Main function to iterate through all accounts and apply the policy."""
    accounts = list_accounts()
    for account in accounts:
        account_id = account["Id"]
        account_name = account["Name"]

        print(f"\n[INFO] Processing account: {account_name} ({account_id})")
        iam_client = assume_role(account_id)
        if not iam_client:
            continue

        enforce_password_policy(iam_client)

if __name__ == "__main__":
    main()
