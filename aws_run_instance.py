#!/usr/bin/env python

from flask import Flask, request
import json, boto3

port = 8080
ami_id = 'ami-3e713f4d'
ec2 = boto3.resource('ec2')

app = Flask(__name__)
@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/createvm', methods=['POST'])
def create_vm():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        abort(400)

    credentials = {
        'username': request.json['username'],
        'password': request.json.get('password'),
    }

    instance_id = ec2.create_instances(
                        ImageId = ami_id,
                        MinCount = 1,
                        MaxCount = 1,
                        KeyName = 'bogdan',
                        InstanceType = 't2.micro',
                    )[0].id

    instance = ec2.Instance(instance_id)
    instance.wait_until_running()

    return json.dumps({'instance_id': instance_id, 'instance_ip': instance.public_ip_address}), 201

if __name__ == "__main__":
    app.run(port=port, debug=True)
