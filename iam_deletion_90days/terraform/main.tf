provider "aws" {
  region = "us-east-1"  # Change to your preferred AWS region
}

# S3 Bucket for Lambda Deployment
resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "lambda-function-deployment-bucket-ne3383"
  force_destroy = true
}

# IAM Role for Lambda Execution
resource "aws_iam_role" "lambda_role" {
  name = "iam_user_cleanup_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda Permissions
resource "aws_iam_policy" "lambda_policy" {
  name        = "iam_user_cleanup_policy"
  description = "Policy for IAM user cleanup function"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "organizations:ListAccounts",
          "sts:AssumeRole",
          "iam:ListUsers",
          "iam:GetUser",
          "iam:ListUserTags",
          "iam:ListAccessKeys",
          "iam:ListAttachedUserPolicies",
          "iam:DeleteUser",
          "iam:DeleteLoginProfile",
          "iam:DeleteAccessKey",
          "iam:DetachUserPolicy",
          "ses:SendEmail"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Attach IAM Policy to Lambda Role
resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Zip the Lambda Function Code
data "archive_file" "lambda_package" {
  type        = "zip"
  source_file = "delete_inactive_iam_users_lambda.py"
  output_path = "delete_inactive_iam_users_lambda.zip"
}

# Upload Zip File to S3
resource "aws_s3_object" "lambda_zip" {
  bucket = aws_s3_bucket.lambda_bucket.id
  key    = "delete_inactive_iam_users_lambda.zip"
  source = data.archive_file.lambda_package.output_path
  etag   = filemd5(data.archive_file.lambda_package.output_path)
}

# Lambda Function
resource "aws_lambda_function" "iam_user_cleanup" {
  function_name    = "delete_inactive_iam_users"
  role            = aws_iam_role.lambda_role.arn
  handler         = "delete_inactive_iam_users_lambda.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300
  memory_size     = 256

  s3_bucket       = aws_s3_bucket.lambda_bucket.id
  s3_key          = aws_s3_object.lambda_zip.key

  environment {
    variables = {
      SES_REGION   = "us-east-1"
      EMAIL_SENDER = "noreply@yourcompany.com" //replace with our SES handler
    }
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_policy_attach]
}

# CloudWatch Event Rule (Runs Daily)
resource "aws_cloudwatch_event_rule" "daily_lambda_trigger" {
  name        = "daily_iam_cleanup"
  description = "Triggers the IAM cleanup Lambda function daily"
  schedule_expression = "rate(1 day)"  # Runs once per day
}

# CloudWatch Event Target (Triggers Lambda)
resource "aws_cloudwatch_event_target" "lambda_trigger" {
  rule      = aws_cloudwatch_event_rule.daily_lambda_trigger.name
  target_id = "lambda"
  arn       = aws_lambda_function.iam_user_cleanup.arn
}

# Lambda Permission for EventBridge
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.iam_user_cleanup.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_lambda_trigger.arn
}

# SES Email Identity (Email Verification Required)
resource "aws_ses_email_identity" "email_identity" {
  email = "noreply@yourcompany.com" //replace with our SES handler
}
