from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

SETTINGS = {
    "client_name": "PeopleCounter_cogni",
    "https_endpoint": "some-endpoint.iot.us-east-1.amazonaws.com",
    "port": 8883,
    "root_cert": "certs.awsiot/VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem",
    "private_key": "certs.awsiot/some-id-private.pem.key",
    "thing_cert": "certs.awsiot/some-id-certificate.pem.crt"
}

client = AWSIoTMQTTClient(SETTINGS["client_name"])
client.configureEndpoint(SETTINGS["https_endpoint"], SETTINGS["port"])
client.configureCredentials(SETTINGS["root_cert"], SETTINGS["private_key"], SETTINGS["thing_cert"])
client.configureOfflinePublishQueueing(-1);
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(10)
client.configureMQTTOperationTimeout(5)
client.connect()

print("Yay!")
