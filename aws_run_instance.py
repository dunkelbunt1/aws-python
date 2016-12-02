#!/usr/bin/env python3

from flask import Flask
from flask import request
import json 
import boto3

app = Flask(__name__)

@app.route('/')

def index():
    return "Hello world"

@app.route('/createvm', methods=['POST'])

def hello():
    if not request.json or not 'username' in request.json:
        abort(400)
    credentials = {
        'username': request.json['username'],
        'password': request.json['password'],
    }
    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
	ImageId='ami-3e713f4d',
	MinCount=1, 
	MaxCount=1,
        KeyName='KeyName',
	InstanceType = 't2.micro',
    )

    return json.dumps({'instance_id': instance[0].id}), 201

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True) 
