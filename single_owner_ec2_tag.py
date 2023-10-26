import json
import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    print(event)
    instanceid = event['detail']['responseElements']['instancesSet']['items'][0]['instanceId']
    username = (event['detail']['userIdentity']['arn']).split("/")
    user = username[2]
    ec2.create_tags(
        Resources=[
            instanceid
            ],
        Tags=[
            {
                'Key': 'Owner',
                'Value': user
            }
            ]
        )
    return
