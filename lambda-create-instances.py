import json, boto3, time

aws_access_key_id = ''
aws_secret_access_key = ''
region_name = 'sa-east-1'

ec2 = boto3.resource('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)


def lambda_handler(event, context):
    id_exec = event["id_exec"]
    
    user_data = f'''#!/bin/bash
    cd /home/ec2-user
    sudo yum update -y
    sudo yum install java-17-amazon-corretto -y
    export AWS_ACCESS_KEY_ID=AKIA23HSILAQM5FUV5E5
    export AWS_SECRET_ACCESS_KEY=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
    export AWS_DEFAULT_REGION=us-east-1
    aws s3 cp s3://bucket-rdf/jar/{id_exec} /home/ec2-user/sddms --recursive #id ao invez de origin
    cd sddms
    java -jar sddms-0.0.1-SNAPSHOT.jar
    '''

    instance = ec2.create_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sdh',
                'Ebs': {
                    'DeleteOnTermination': True,
                    'VolumeSize': 8,
                    'VolumeType': 'gp3'
                }
            }
        ],
        ImageId='ami-04cf3e80f9795a29b',
        InstanceType='t2.micro',
        KeyName='ec2-first-instance',
        SecurityGroupIds=[
            'sg-05079442696769266'
        ],
        SecurityGroups=[
            'launch-wizard-4'
        ],
        IamInstanceProfile={
            'Name': 'ec2-demo-role'
        },
        MaxCount=1,
        MinCount=1,
        Monitoring={
            'Enabled': False
        },
        UserData=user_data
    )
    instance = instance[0]

    while instance.public_dns_name == "":
        instance.reload()
    
    instance_public_dns = instance.public_dns_name
        

    return {
        'statusCode': 200,
        'body': json.dumps(f'http://{instance_public_dns}:8080/sddms')
    }

