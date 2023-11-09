import time
import re
import boto3

ec2_client = boto3.client('ec2')

def ebs_volume_id(volume_arn):
    arn_parts = volume_arn.split(':')
    volume_id = arn_parts[-1].split('/')[-1]
    return volume_id


def create_encrypted_volume(volume_id, region, az):
    '''pass the volume_id,region,az to encrpt the volume'''
    snapshot_id = (ec2_client.create_snapshot(
        Description=f'This is {volume_id} volume snapshot.',
        VolumeId=volume_id,
    ))['SnapshotId']
    print(snapshot_id)
    time.sleep(30)
    encrypted_snapshot_id = (ec2_client.copy_snapshot(
        Description='Encrypted snapshot for ' + snapshot_id,
        Encrypted=True,
        KmsKeyId='alias/aws/ebs',
        SourceRegion=region,
        SourceSnapshotId=snapshot_id,
    ))['SnapshotId']
    print(encrypted_snapshot_id)
    time.sleep(30)
    new_volume_id = ec2_client.create_volume(
        AvailabilityZone=az,
        SnapshotId=encrypted_snapshot_id,
        VolumeType='gp3',
    )['VolumeId']
    time.sleep(30)
    delete_temp_snapshot([snapshot_id, encrypted_snapshot_id])
    return new_volume_id


def delete_temp_snapshot(snapshot_ids):
    for snapshot_id in snapshot_ids:
        response = ec2_client.delete_snapshot(
            SnapshotId=snapshot_id, )


def lambda_handler(event, context):
    volume_arn = event['resources'][0]
    print(volume_arn)
    volume_id = ebs_volume_id(volume_arn)
    encrypt_response = ec2_client.describe_volumes(VolumeIds=[volume_id])
    az = encrypt_response['Volumes'][0]['AvailabilityZone']
    region = re.search(r'^[a-z]+-[a-z]+-\d+', az).group(0)
    print(region)
    if 'Volumes' in encrypt_response:
        volume = encrypt_response['Volumes'][0]
        encrypted = volume['Encrypted']
        vol_type = encrypt_response['Volumes'][0]['VolumeType']
        if encrypted:
            if vol_type == 'gp3':
                print(f"{volume_id} looks good")
            else:
                print(f"The volume {volume_id} is encrypted, but not a gp3. So modifying to gp3")
                response = ec2_client.modify_volume(
                    VolumeId=volume_id,
                    VolumeType='gp3', )
        else:
            print(f"{volume_id} is not encrypted and not gp3. So performing both actions")
            create_encrypted_volume(volume_id, region, az)
            response = ec2_client.delete_volume(VolumeId=volume_id)
    else:
        print(f"Volume {volume_id} not found.")