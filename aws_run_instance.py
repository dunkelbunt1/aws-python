#!/usr/bin/env python3
import sys
import time
from flask import Flask, request
import json, boto3, botocore
import paramiko
import crypt

port = 8080
ami_id = 'ami-dd3c0f36'
instance_type = 't2.micro'
keyname  = 'mykey'
username = 'centos'
pkey_file = '~/.ssh/mykey.pem'

ec2 = boto3.resource('ec2')

def create_instance():
    try:
        sg  = ec2.create_security_group(Description='My Security Group', GroupName='mysg', DryRun=False)
        sg.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)
        print ("Creating AWS Secury Group to allow SSH access...")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "InvalidGroup.Duplicate":
            print ("Security Group already exists.")
            pass
    print ("Creating AWS EC2 instance...")
    data = {}
    instance_id = ec2.create_instances(
                        ImageId = ami_id,
                        MinCount = 1,
                        MaxCount = 1,
                        KeyName = keyname,
                        InstanceType = instance_type,
                    )[0].id
    instance = ec2.Instance(instance_id)
    instance.wait_until_running(Filters=[{'Name': 'instance-state-name', 'Values': ['running',]},],)
    data['instance_id'] = instance_id
    data['instance_ip'] = instance.public_ip_address
    return data

def adduser(connection,username,password,sudo=False):
    shadow_password = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))
    print("Adding user...")
    command = "sudo useradd -m " + username + " -p " + shadow_password
    return connection.exec_command(command)

def connect(host):
    key = paramiko.RSAKey.from_private_key_file(pkey_file)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print ("Connecting to EC2 instance...")
    time.sleep(30)
    ssh.connect(hostname = host, username = username, pkey = key)
    print ("Connection established.")
    ip = create_instance()
    print (ip)
    ssh.close()

app = Flask(__name__)

@app.route('/create', methods=['POST'])
def main():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        abort(400)
    credentials = {
        'username': request.json['username'],
        'password': request.json['password'],
    }
    node = create_instance()
    c = connect(node['instance_ip'])
    return json.dumps(c)

if __name__ == "__main__":
    app.run(port=port, debug=True)
