# AWS IAM User Cleanup Lambda - Terraform Deployment

## Overview
This Terraform script provisions an AWS Lambda function that automatically cleans up inactive IAM users. The function is deployed using AWS Lambda, scheduled to run daily via Amazon EventBridge (CloudWatch Events), and uses AWS SES to send email notifications.

## Resources Created
- **AWS S3 Bucket**: Stores the Lambda function package.
- **IAM Role & Policy**: Grants the Lambda function permissions to manage IAM users and send emails via SES.
- **Lambda Function**: Executes the cleanup of inactive IAM users.
- **CloudWatch Event Rule**: Triggers the Lambda function daily.
- **SES Email Identity**: Configures an email sender for notifications.

## Prerequisites
- **Terraform Installed**: Ensure you have Terraform installed ([Download Terraform](https://developer.hashicorp.com/terraform/downloads)).
- **AWS CLI Configured**: Run `aws configure` to set up credentials.
- **SES Email Verification**: The sender email must be verified in AWS SES.

## Deployment Instructions
### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Update Configuration
Modify the following parameters in the `main.tf` file as needed:
- **AWS Region** (`provider "aws" { region = "us-east-1" }`)
- **S3 Bucket Name** (`lambda-function-deployment-bucket`)
- **SES Sender Email** (`noreply@yourcompany.com`)

### 3. Initialize Terraform
```bash
terraform init
```

### 4. Plan the Deployment
```bash
terraform plan
```

### 5. Apply the Deployment
```bash
terraform apply -auto-approve
```

## Functionality
1. **Daily Execution**: The Lambda function runs once per day to check for inactive IAM users.
2. **IAM User Cleanup**:
   - Lists IAM users.
   - Identifies inactive users.
   - Deletes inactive IAM users and associated credentials.
3. **Email Notifications**: Sends an email using AWS SES when users are removed.

## Cleanup
To remove all deployed resources, run:
```bash
terraform destroy -auto-approve
```

## Notes
- Ensure SES email identity is verified before deployment.
- If using a different AWS region, update the `SES_REGION` environment variable in the Lambda function.

## Troubleshooting
- **Lambda Execution Errors**: Check AWS CloudWatch Logs.
- **IAM Role Issues**: Ensure the IAM role has the correct permissions.
- **SES Email Issues**: Verify the email sender in AWS SES.

## License
This project is licensed under the MIT License.

---

**Author:** Nate Embree  
**Department:** Infrastructure Development 

