## aws-boto3-projects
Simple python boto3 scripts for day to-day activities

**single_owner_ec2_tag.py**

There are some use cases when people create an EC2, but forget to tag the owner. This script will automatically fetches the information from CloudWatch and assign the tag to an instance.
Note: This is applicable for single EC2 instance only and you have to attach EventBride(CloudWatch Events) to this lambda function to trigger when EC2 created without tag.

**Event Pattern:**

{
  "source": ["aws.ec2"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": ["ec2.amazonaws.com"],
    "eventName": ["RunInstances"]
  }
}

**ebs_volume_encryption_and_type_check.py**

When you're in production environment - often people create volumes with GP2 and most of the time its not encrypted. 
You can use this script in lambda to automatically convert the volume to gp3 and encrypt the volume using aws default key in EBS volume creation.
Make sure you have to attach EventBride rule(EBS Volume Notification/createVolume) to trigger this lambda function.
