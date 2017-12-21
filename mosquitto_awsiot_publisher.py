from __future__ import print_function
import paho.mqtt.client as paho_mqtt
import argparse, json
import mosquitto_awsiot_config


# arguments
parser = argparse.ArgumentParser()
parser.add_argument('--mosquitto_config_path', type=str, default='./config/mosquitto.json', help='Path to mosquitto config json.')
parser.add_argument('--message', type=str, default=None, help='A message to publish.') 
parser.add_argument('--topic', type=str, default='events/test', help='A topic for publishing.') 
args = parser.parse_args()

# configuration
mosquitto = mosquitto_awsiot_config.get_mosquitto_config(config_path=args.mosquitto_config_path)

# message to publish
msg = { 'body': (args.message if args.message else 'Hello world!') }
payload = json.dumps(msg)
topic = args.topic

# publish events to mosquitto
mosquitto_client = paho_mqtt.Client()
mosquitto_client.tls_set(mosquitto.cacert, certfile=mosquitto.cert, keyfile=mosquitto.keyfile)
mosquitto_client.connect(mosquitto.host, mosquitto.port, mosquitto.keepalive)
mosquitto_client.publish(topic, payload)
mosquitto_client.disconnect()

