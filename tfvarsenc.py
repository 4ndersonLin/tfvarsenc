# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:   
# https://aws.amazon.com/developers/getting-started/python/
import sys
import json
import os
import boto3
from botocore.exceptions import ClientError
secret_name = "tfvars"
endpoint_url = "https://secretsmanager.ap-southeast-1.amazonaws.com"
region_name = "ap-southeast-1"

def get_secret():


    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        endpoint_url=endpoint_url
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
    else:
        # Decrypted secret using the associated KMS CMK
        # Depending on whether the secret was a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            binary_secret_data = get_secret_value_response['SecretBinary']
            return binary_secret_data

def put_secret(tfvars_value):

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        endpoint_url=endpoint_url
    )
    print(tfvars_value)
    try:
        put_secret_value_response = client.put_secret_value(
            SecretId=secret_name,
            SecretString=tfvars_value
        )
        #print(put_secret_value_response)

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
    else:
        print("Put success")

def __main__():
    if sys.argv[1] == 'get':
        print("Get secret")
        tfvars = json.loads(get_secret())['tfvars']
        decode_tfvars = bytes(tfvars, "utf-8").decode("unicode_escape")
        f = open("secret.tfvars", "w")
        f.write(decode_tfvars)
        f.close()

    elif sys.argv[1] == 'put':
        print("Put secret")
        f = open('secret.tfvars', 'r')
        with f as myfile:
            data=myfile.read()
        f.close()
        print(data)
        tfvars_json = {
            "tfvars" : data
        }
        print(tfvars_json)
        put_secret(json.dumps(tfvars_json))
        try:
            os.remove('secret.tfvars')
        except OSError:
            print('Delete secret.tfvars error')

    elif sys.argv[1] == 'plan':
        print("terraform plan with secret")
        print(sys.argv[2:])
        args = ''
        for arg in sys.argv[2:]:
            args += arg +' '
        plan_arg = 'terraform plan ' + args + '-var-file="secret.tfvars"'
        print(plan_arg)
        os.system(plan_arg)

    elif sys.argv[1] == 'apply':
        print("terraform apply with secret")
        print(sys.argv[2:])
        args = ''
        for arg in sys.argv[2:]:
            args += arg +' '
        apply_arg = 'terraform apply ' + args + '-var-file="secret.tfvars"'
        print(apply_arg)
        os.system(apply_arg)
    
    else:
        print("Unsupport operation")

if __name__ == '__main__':
    __main__()