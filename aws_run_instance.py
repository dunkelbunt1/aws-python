#!/usr/bin/env python3

from flask import Flask, request
import json, boto3

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
    return json.dumps(vm)

if __name__ == "__main__":
    app.run(port=port, debug=True)
