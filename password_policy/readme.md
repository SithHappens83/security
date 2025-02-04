# AWS Password Policy Enforcement Script

## Overview

This script enforces a standard password policy across all AWS accounts in an AWS Organization. It retrieves all accounts within the organization, assumes a predefined IAM role in each account, and updates the account's password policy accordingly.

## Features

- Lists all AWS accounts in an organization using AWS Organizations.
- Assumes an IAM role (`OrganizationAccountAccessRole`) in each account.
- Updates the password policy with predefined security settings.
- Logs success and error messages for each account.

## Prerequisites

1. **AWS Credentials:** Ensure your AWS CLI is configured with credentials that have permission to call AWS Organizations and STS.
2. **IAM Role:** Each AWS account must have the IAM role `OrganizationAccountAccessRole` or an equivalent role with permission to update the password policy.
3. **Python 3.x** and **boto3** installed.

## Installation

1. Clone this repository or download the script.
2. Install the required dependencies:

   ```bash
   pip install boto3
   ```

3. Ensure your AWS credentials are properly configured using:

   ```bash
   aws configure
   ```

## Configuration

The password policy settings are defined in the `PASSWORD_POLICY` dictionary within the script:

   ```python
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
   ```

Modify these settings as needed to align with your security policies.

## Updating the Configuration

If you need to modify the password policy, follow these steps:

1. Open the script file (`enforce_password_policy.py`).
2. Locate the `PASSWORD_POLICY` dictionary.
3. Update the required settings. For example, to change the minimum password length to 12 characters, modify this line:

   ```python
   "MinimumPasswordLength": 12,
   ```

4. Save the file.
5. Re-run the script to apply the updated policy:

   ```bash
   python enforce_password_policy.py
   ```

## Usage

Run the script using:

   ```bash
   python enforce_password_policy.py
   ```

### Script Execution Flow

1. **Retrieve AWS Accounts** – The script fetches all AWS accounts in the organization.
2. **Assume IAM Role** – It assumes the `OrganizationAccountAccessRole` in each account.
3. **Apply Password Policy** – The password policy is updated based on predefined settings.

## Logging and Error Handling

- `[INFO]` messages indicate the progress of applying policies.
- `[SUCCESS]` messages indicate successful updates.
- `[ERROR]` messages indicate failures and will include the specific reason.

## Troubleshooting

- **Permission Issues:** Ensure your AWS CLI user and `OrganizationAccountAccessRole` have permissions for:
  - `organizations:ListAccounts`
  - `sts:AssumeRole`
  - `iam:UpdateAccountPasswordPolicy`
- **AWS Profile Issues:** If using multiple AWS profiles, specify a profile:

   ```bash
   AWS_PROFILE=my-profile python enforce_password_policy.py
   ```

- **Network Issues:** Ensure you have network access to AWS endpoints.

## Security Considerations

- Do **not** hardcode credentials in the script.
- Ensure the IAM role has the minimum necessary permissions.
- Regularly review password policy settings to comply with security standards.

## License

This script is licensed under the MIT License.

---

**Author:** Nate Embree  
**Department:** Infrastructure Development 
