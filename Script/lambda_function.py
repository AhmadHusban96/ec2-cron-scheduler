"""
EC2CronScheduler Lambda Function

Created by Ahmad Husban
GitHub: https://github.com/AhmadHusban96/ec2-cron-scheduler
LinkedIn: https://www.linkedin.com/in/ahmad-husban/

This Lambda function manages EC2 instances based on cron schedules. It automatically starts and stops
EC2 instances based on specified cron expressions, ensuring that your instances are only running when needed.
"""

import boto3
import logging
from datetime import datetime
from croniter import croniter
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_all_regions():
    """Fetch all available AWS regions."""
    # Initialize EC2 client for metadata
    ec2_metadata_client = boto3.client('ec2', region_name='us-east-1')  # Default region for metadata
    # Get the list of all AWS regions
    regions = [region['RegionName'] for region in ec2_metadata_client.describe_regions()['Regions']]
    return regions

def get_instances_in_region(region):
    """Fetch all EC2 instances in the given region."""
    # Initialize EC2 client for the specified region
    ec2_client = boto3.client('ec2', region_name=region)
    # Use paginator to handle large sets of instances
    paginator = ec2_client.get_paginator('describe_instances')
    instances = []
    # Iterate through all pages of instance descriptions
    for page in paginator.paginate():
        for reservation in page['Reservations']:
            instances.extend(reservation['Instances'])
    return instances, ec2_client

def evaluate_instance(instance, current_time):
    """Evaluate the instance based on its tags and the current time."""
    instance_id = instance['InstanceId']
    # Convert list of tags to a dictionary for easier access
    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}

    works_on_schedule = tags.get('WorksOnSchedule')
    working_expression = tags.get('WorkingExpression')
    
    # Skip instance if 'WorksOnSchedule' tag is missing or not set to 'true'
    if works_on_schedule is None or works_on_schedule.lower() != 'true':
        return None, f"Skipping instance {instance_id}: 'WorksOnSchedule' tag is missing or not true."

    # Skip instance if 'WorkingExpression' tag is missing or empty
    if working_expression is None or working_expression == '':
        return None, f"Skipping instance {instance_id}: 'WorkingExpression' tag is missing or empty."

    try:
        # Check if the cron expression is valid
        if croniter.is_valid(working_expression):
            # Match current time with the cron expression
            if croniter.match(working_expression, current_time):
                return 'start', f"Starting instance {instance_id}: Current time matches cron expression."
            else:
                return 'stop', f"Stopping instance {instance_id}: Current time does not match cron expression."
        else:
            return None, f"Skipping instance {instance_id}: Invalid cron expression '{working_expression}'."
    except Exception as e:
        # Log any error that occurs during evaluation
        return None, f"Error evaluating instance {instance_id}: {str(e)}"

def exponential_backoff(func, **kwargs):
    """Retry function with exponential backoff on failure."""
    max_retries = 5  # Maximum number of retries
    base_delay = 1   # Initial delay in seconds
    max_delay = 32   # Maximum delay in seconds

    for attempt in range(max_retries):
        try:
            # Attempt to call the function
            return func(**kwargs)
        except Exception as e:
            if attempt < max_retries - 1:
                # Calculate delay with exponential backoff and jitter
                sleep_time = min(base_delay * 2 ** attempt, max_delay) + random.uniform(0, 1)
                logger.warning(f"Error calling {func.__name__} with args {kwargs}: {str(e)}. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)  # Wait before retrying
            else:
                # Log error if maximum retries are reached
                logger.error(f"Error calling {func.__name__} with args {kwargs}: {str(e)}. No more retries left.")
                raise

def process_region(region, current_time):
    """Process all instances in a specific region."""
    instances, ec2_client = get_instances_in_region(region)
    start_instances = []
    stop_instances = []
    messages = []
    
    for instance in instances:
        # Evaluate each instance to determine action
        action, message = evaluate_instance(instance, current_time)
        if action == 'start':
            start_instances.append(instance['InstanceId'])
        elif action == 'stop':
            stop_instances.append(instance['InstanceId'])
        messages.append(message)
    
    return start_instances, stop_instances, ec2_client, messages

def batch_start_instances(ec2_client, instance_ids):
    """Batch start instances."""
    for i in range(0, len(instance_ids), 50):
        # Start instances in batches of 50 to reduce API calls
        exponential_backoff(ec2_client.start_instances, InstanceIds=instance_ids[i:i+50])

def batch_stop_instances(ec2_client, instance_ids):
    """Batch stop instances."""
    for i in range(0, len(instance_ids), 50):
        # Stop instances in batches of 50 to reduce API calls
        exponential_backoff(ec2_client.stop_instances, InstanceIds=instance_ids[i:i+50])

def lambda_handler(event, context):
    """Main Lambda function handler."""
    regions = get_all_regions()  # Get all AWS regions
    current_time = datetime.now()  # Get the current time
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Process each region in parallel
        future_to_region = {executor.submit(process_region, region, current_time): region for region in regions}
        for future in as_completed(future_to_region):
            region = future_to_region[future]
            try:
                # Collect results from each region
                start_instances, stop_instances, ec2_client, messages = future.result()
                results.append((start_instances, stop_instances, ec2_client, messages))
            except Exception as e:
                logger.error(f"Error processing region {region}: {str(e)}")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for start_instances, stop_instances, ec2_client, messages in results:
            for message in messages:
                logger.info(message)
            if start_instances:
                # Batch start instances in parallel
                futures.append(executor.submit(batch_start_instances, ec2_client, start_instances))
            if stop_instances:
                # Batch stop instances in parallel
                futures.append(executor.submit(batch_stop_instances, ec2_client, stop_instances))
        
        for future in as_completed(futures):
            try:
                # Ensure all futures complete successfully
                future.result()
            except Exception as e:
                logger.error(f"Error executing batch operation: {str(e)}")
