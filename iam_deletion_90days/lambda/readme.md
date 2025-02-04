# AWS IAM User Cleanup Script

This AWS Lambda script automates the management of inactive IAM users across an AWS Organization. It detects inactive IAM users, sends warning emails via AWS SES, and deletes users who exceed the inactivity threshold.

## Features

- **Assume Role in Each AWS Account**: Uses `OrganizationAccountAccessRole` to access IAM users in member accounts.
- **Detects Inactive Users**: Checks the last login date of IAM users.
- **Sends Warning Emails**: Notifies inactive users via AWS SES before deletion.
- **Deletes Inactive Users**: Removes IAM users after a predefined inactivity period.

## Prerequisites

- AWS Organizations must be enabled.
- AWS IAM roles must be configured to allow cross-account access.
- AWS SES must be set up for sending emails.
- IAM users should have an "email" tag for notifications.

## Configuration

Set the following environment variables:

| Variable      | Description                                      | Default Value    |
|--------------|--------------------------------------------------|------------------|
| `SES_REGION` | AWS SES region for sending emails               | `us-east-1`      |
| `EMAIL_SENDER` | Sender email address for SES notifications      | `noreply@yourcompany.com` |
| `WARNING_DAYS` | Days of inactivity before sending warnings      | `60`             |
| `DELETION_DAYS` | Days of inactivity before user deletion       | `90`             |

## How It Works

1. **List AWS Accounts**: The script retrieves all accounts in the AWS Organization.
2. **Assume Role**: It assumes the `OrganizationAccountAccessRole` in each account.
3. **Check IAM Users**:
   - If a user has never logged in, it is skipped.
   - If inactive for `WARNING_DAYS`, an email notification is sent.
   - If inactive for `DELETION_DAYS`, the user is deleted.
4. **Delete User**:
   - Deletes login profile, attached policies, access keys, and then the user account.

## Deployment

1. Create an AWS Lambda function.
2. Upload the script as a ZIP file.
3. Set up the required IAM permissions.
4. Configure environment variables.
5. Schedule the Lambda function using Amazon EventBridge (e.g., run daily).

## Logging & Error Handling

- Logs errors if it fails to assume roles, list users, send emails, or delete users.
- Warnings are logged if a user's email is missing.

## Security Considerations

- Ensure IAM permissions are scoped to only required actions.
- Use AWS CloudWatch Logs for monitoring.
- Configure AWS SES for email sending permissions.

## Author

- Author - Nate Embree
- Infrastructure Development Team - 360Instights

---

For any issues, contact our security team.
