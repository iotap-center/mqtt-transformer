
# AWS IoT Thing


https://docs.aws.amazon.com/iot/latest/developerguide/iot-sdk-setup.html


## Register an AWS IoT Thing

```
sceneclassifier
arn:aws:iot:eu-west-1:859045276223:thing/sceneclassifier
```

## Security 

In order to connect a device, you need to download the following:
- A certificate for this thing    4378cd1300.cert.pem Download
- A public key    4378cd1300.public.key   Download
- A private key   4378cd1300.private.key  Download

You also need to download a root CA for AWS IoT from Symantec:
- A root CA for AWS IoT   Download

## Create Policy

```
arn:aws:iot:eu-west-1:859045276223:policy/sceneclassifier_policy

{
  "Version": "2012-10-17",
  "Statement": [
  {
    "Effect": "Allow",
    "Action": "iot:*",
    "Resource": "*"
  }
  ]
}
```

## Attach Policy and Thing to Certificate

Goto: Security -> Certificates 

Use checkbox menu to:
1. Attach Policy
2. Attach Thing


## Interact

```
HTTPS
a1y7d41s0oj85v.iot.eu-west-1.amazonaws.com

MQTT
Update to this thing shadow

$aws/things/sceneclassifier/shadow/update
Update to this thing shadow was accepted

$aws/things/sceneclassifier/shadow/update/accepted
Update this thing shadow documents

$aws/things/sceneclassifier/shadow/update/documents
Update to this thing shadow was rejected

$aws/things/sceneclassifier/shadow/update/rejected
Get this thing shadow

$aws/things/sceneclassifier/shadow/get
Get this thing shadow accepted

$aws/things/sceneclassifier/shadow/get/accepted
Getting this thing shadow was rejected

$aws/things/sceneclassifier/shadow/get/rejected
Delete this thing shadow

$aws/things/sceneclassifier/shadow/delete
Deleting this thing shadow was accepted

$aws/things/sceneclassifier/shadow/delete/accepted
Deleting this thing shadow was rejected

$aws/things/sceneclassifier/shadow/delete/rejected
```

-----

# AWS IoT SDKs



## AWS IoT Python SDK

Install aws iot python sdk:
```bash
sudo pip install AWSIoTPythonSDK
```

Configure using *aws thing cert* method and *TLS mutual auth* protocol:
```python
# TLS Mutual Auth on port 8883
clientName = "sceneClassificationClient"
httpsEndpoint = "a1y7d41s0oj85v.iot.eu-west-1.amazonaws.com"
rootCert = certsDir + "VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem"
privateKey = certsDir + "4378cd1300-private.pem.key"
thingCert = certsDir + "4378cd1300-certificate.pem.crt"
```

https://github.com/aws/aws-iot-device-sdk-python

https://github.com/aws/aws-iot-device-sdk-python/blob/master/samples/basicPubSub/basicPubSub.py


## AWS IoT C SDK

https://github.com/aws/aws-iot-device-sdk-embedded-C

https://docs.aws.amazon.com/iot/latest/developerguide/iot-embedded-c-sdk.html



