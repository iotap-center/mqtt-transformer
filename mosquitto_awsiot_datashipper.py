from __future__ import print_function
import paho.mqtt.client as paho_mqtt
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time, argparse, re, json
import mosquitto_awsiot_config
import socket


# arguments
parser = argparse.ArgumentParser()
parser.add_argument('--mosquitto_config_path', type=str, default='/home/pi/IoT/mosquitto_awsiot_datashipper/config/mosquitto.json', help='Path to mosquitto config json.')
parser.add_argument('--awsiot_config_path', type=str, default='/home/pi/IoT/mosquitto_awsiot_datashipper/config/awsiot.json', help='Path to awsiot config json.')
args = parser.parse_args()


# configuration
mosquitto = mosquitto_awsiot_config.get_mosquitto_config(config_path=args.mosquitto_config_path)
awsiot = mosquitto_awsiot_config.get_mosquitto_config(config_path=args.awsiot_config_path)
print(awsiot)

# setup client
print("setting up client")
awsiot_client = AWSIoTMQTTClient(awsiot.client_name) # certificate based connection
awsiot_client.configureEndpoint(awsiot.https_endpoint, awsiot.port) # TLS mutual authentication
awsiot_client.configureCredentials(awsiot.root_cert, awsiot.private_key, awsiot.thing_cert)
awsiot_client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
awsiot_client.configureDrainingFrequency(2)  # Draining: 2 Hz
awsiot_client.configureConnectDisconnectTimeout(10)  # 10 sec
awsiot_client.configureMQTTOperationTimeout(5)  # 5 sec
awsiot_client.connect()
print("I'm alive")
time.sleep(2)


'''
get the thing name from topic
assuming
topic: status/<DeviceType>/<MAC>/<AppName>/<AppId>/<type>
thing name: <AppName><AppId><MAC>
'''
def get_thing_name(topic):
    if topic.count('/') != 5:
        return None
    topic = topic.split('/')
    return "{name}{id}{mac}".format(name=topic[3], id=topic[4], mac=topic[2])

'''
assuming
topic: camera/<MAC>/<AppName>/<AppId>/<type>
thing name <AppName><AppId><MAC>
'''
def get_thing_name_2(topic):
    if topic.count('/') != 4:
        return None
    topic = topic.split('/')
#    return "{name}{id}{mac}".format(name=topic[2], id=topic[3], mac=topic[1])
    return "camera" + topic[1]

# subscriber callback relaying messages to awsiot
def on_message(client, userdata, msg):
    print("Message received: ")
    if msg.topic.startswith("status/camera/"):
        return # This is, currently, of no use for CoSIS
        name = get_thing_name(msg.topic)
        if name is None:
            print("Unknown status topic: {}".format(msg.topic))
            return
        status = msg.topic.split('/')[-1]
        print(msg.payload)
        shadow_topic = name + "/things/{}/shadow/update"
        shadow_payload = '{ "state" : { "reported" : { "%s" : "%s" } } }' % (status, msg.payload)
        print("Updated status {thing}.{status} to '{value}'".format(thing=name, status=status, value=msg.payload))
        awsiot_client.publish(shadow_topic, shadow_payload, 0)
        return
    elif re.match("^camera\/.+\/AXIS", msg.topic):
        name = get_thing_name_2(msg.topic)
        if name is None:
            print("Unknown status topic: {}".format(msg.topic))
            return
        shadow_topic = "IoTaP-lab/Raspberry/" + name + "/multiple"
        shadow_payload = json.dumps({ 'timestamp': round(time.time(), 2), 'd': { 'name': name, 'passage': msg.payload.decode("utf-8")}})
        print("Reported event " + shadow_payload)
        awsiot_client.publish(shadow_topic, shadow_payload, 0)
        return
    print(msg.topic, " ", str(msg.payload))
    awsiot_client.publish(msg.topic, msg.payload, 0)


# subscribe on events published to mosquitto
mosquitto_client = paho_mqtt.Client()
if mosquitto.use_cert:
    mosquitto_client.tls_set(mosquitto.cacert, certfile=mosquitto.cert, keyfile=mosquitto.keyfile)
mosquitto_client.on_message = on_message
mosquitto_client.connect(mosquitto.host, mosquitto.port, mosquitto.keepalive)
mosquitto_client.subscribe(mosquitto.topic)
mosquitto_client.loop_forever()

# disconnect awsiot
awsiot_client.disconnect()


