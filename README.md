# EC2 Cron Scheduler

## Overview

This repository contains a solution for automating the scheduling of EC2 instances across all AWS regions using AWS Lambda and EC2 tags with CRON expressions. This approach simplifies cloud management and optimizes costs by allowing you to manage instance schedules with a single Lambda function.

## Features

- Automates starting and stopping of EC2 instances based on CRON expressions.
- Manages multiple schedules across different AWS regions with a single solution.
- Easy to update schedules by simply modifying EC2 instance tags.

## Deployment Options

You have multiple choices for deploying this solution:

1. **Manual Creation**: Follow the detailed step-by-step guide to manually create and configure the Lambda function, IAM roles, and CloudWatch Events.
2. **CloudFormation Template**: Deploy using the provided CloudFormation template. [CloudFormation Template Link](https://github.com/AhmadHusban96/ec2-cron-scheduler/blob/main/CloudFormation/ec2-cron-scheduler.yaml)
3. **Quick Launch Link**: Use this quick launch link to deploy the CloudFormation stack with default parameters: [Quick Launch CloudFormation](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/quickcreate?templateURL=https://ec2-cron-scheduler.s3.amazonaws.com/ec2-cron-scheduler.yaml&stackName=EC2CronScheduler&param_LambdaMemorySize=256&param_LambdaTimeout=300&param_LambdaInvokeRate=rate(1%20minute)&param_S3BucketName=ec2-cron-scheduler&param_S3ObjectKey=EC2CronScheduler.zip)

## Setup Instructions

### 1. Manual Setup

Follow the detailed step-by-step guide in the [Medium article](https://medium.com/@ahmadhusban96/automate-ec2-scheduling-with-aws-lambda-tags-82f8105dc68c).

### 2. CloudFormation Template

- Download the CloudFormation template from the `CloudFormation` folder.
- Deploy the template using the AWS Management Console or AWS CLI.

### 3. Quick Launch

Click on the [Quick Launch Link](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/quickcreate?templateURL=https://ec2-cron-scheduler.s3.amazonaws.com/ec2-cron-scheduler.yaml&stackName=EC2CronScheduler&param_LambdaMemorySize=256&param_LambdaTimeout=300&param_LambdaInvokeRate=rate(1%20minute)&param_S3BucketName=ec2-cron-scheduler&param_S3ObjectKey=EC2CronScheduler.zip) to deploy the stack with default parameters.

## About the Author

Ahmad Husban is a DevOps Specialist and AWS Solutions Architect based in Zarqa, Jordan, with over 4 years of experience in infrastructure automation and continuous integration/deployment processes. Ahmad holds nine AWS certifications, including AWS Certified Solutions Architect – Professional and AWS Certified DevOps Engineer – Professional, as well as the Google Cloud Certified Professional Cloud Architect certification.

Connect with Ahmad on [LinkedIn](https://www.linkedin.com/in/ahmad-husban/) and follow his [GitHub](https://github.com/AhmadHusban96) for more technical content.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Additional Resources

- [Crontab Guru](https://crontab.guru/): Help with CRON expressions.
- [Medium Article](https://medium.com/@ahmadhusban96/automate-ec2-scheduling-with-aws-lambda-tags-82f8105dc68c): Detailed step-by-step guide.
