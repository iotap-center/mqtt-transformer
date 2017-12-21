import os, json
from argparse import Namespace

packagedir = os.path.dirname(os.path.abspath(__file__))

def load_config(path, config={}):
    if path and os.path.isfile(path):
        with open(path,'r') as f:
            user_config = json.load(f)
            config.update(user_config)
    return config

def get_mosquitto_config(config_path=None):
    mosquitto_certdir = packagedir + "/certs.mosquitto/"
    mosquitto_config = {
        'host': 'raspiflow',
        'port': 8883,
        'keepalive': 60,
        'topic': '#',
        'use_cert': 1,
        'cacert': mosquitto_certdir + "ca.crt",
        'cert': mosquitto_certdir + "client.crt",
        'keyfile': mosquitto_certdir + "client.key"
    }
    mosquitto_config = load_config(config_path, config=mosquitto_config)
    return Namespace(**mosquitto_config)

def get_awsiot_config(config_path=None):
    awsiot_certsdir = packagedir + "/certs.awsiot/"
    awsiot_config = {
        'client_name': "sceneClassificationClient",
        'https_endpoint': "some-endpoint.iot.us-east-1.amazonaws.com",
        'port': 1883,
        'root_cert': awsiot_certsdir + "VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem",
        'private_key': awsiot_certsdir + "some-id-private.pem.key",
        'thing_cert': awsiot_certsdir + "some-id-certificate.pem.crt"
    }
    awsiot_config = load_config(config_path, config=awsiot_config)
    return Namespace(**awsiot_config)

