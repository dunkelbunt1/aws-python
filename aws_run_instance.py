#!/usr/bin/env python3
import sys
import time
from flask import Flask, request
import json, boto3
import paramiko
import crypt

port = 8080
ami_id = 'ami-3e713f4d'
keyname = 'bogdan'
instance_type = 't2.micro'

ec2 = boto3.resource('ec2')

def createvm(credentials):
    data = {}
    instance_id = ec2.create_instances(
                        ImageId = ami_id,
                        MinCount = 1,
                        MaxCount = 1,
                        KeyName = keyname,
                        InstanceType = instance_type,
                    )[0].id

    instance = ec2.Instance(instance_id)
    instance.wait_until_running()
    data['instance_id'] = instance_id
    data['instance_ip'] = instance.public_ip_address
    return data

def adduser(connection,username,password,sudo=False):
    shadow_password = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))
    print("Adding user...")
    command = "sudo useradd -m " + username + " -p " + shadow_password
    return connection.exec_command(command)

def connect(host):
    i = 0
    key = paramiko.RSAKey.from_private_key_file("/Users/bodzilla/.ssh/bogdan.pem")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    while True:
        print("Trying to connect to {} ({})".format(host, i))

        try:
            ssh.connect(hostname = host, username = 'ubuntu', pkey = key)
            print("Connected to {}".format(host))
            print("Create a user ...".format(host))
            adduser(ssh, "x1", "xyz123x", sudo=False)
            break
        except paramiko.AuthenticationException:
            print("Authentication failed when connecting to {}".format(host))
            sys.exit(1)
        except:
            print("Could not SSH to {}, waiting for it to start".format(host))
            i += 1
            time.sleep(5)

    # If we could not connect within time limit
        if i == 100:
            print("Could not connect to {}. Giving up".format(host))
            sys.exit(1)

app = Flask(__name__)

@app.route('/createvm', methods=['POST'])
def main():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        abort(400)
    credentials = {
        'username': request.json['username'],
        'password': request.json['password'],
    }
    vm = createvm(credentials)
    c = connect(vm['instance_ip'])
    return json.dumps(c)

if __name__ == "__main__":
    app.run(port=port, debug=True)
