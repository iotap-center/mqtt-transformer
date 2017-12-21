
# Mosquitto MQTT Broker on Raspberry Pi


-----

## Resources

https://mosquitto.org/man/mosquitto-8.html

https://mosquitto.org/man/mosquitto-conf-5.html

https://mosquitto.org/man/mosquitto-tls-7.html

https://mosquitto.org/man/mosquitto_passwd-1.html

http://rockingdlabs.dunmire.org/exercises-experiments/ssl-client-certs-to-secure-mqtt

https://www.baldengineer.com/mqtt-tutorial.html

https://learn.adafruit.com/diy-esp8266-home-security-with-lua-and-mqtt/configuring-mqtt-on-the-raspberry-pi

http://www.hivemq.com/blog/mqtt-essentials-part-5-mqtt-topics-best-practices

http://stackoverflow.com/a/34333973


## Resources - Paho

https://pypi.python.org/pypi/paho-mqtt/1.1

https://eclipse.org/paho/clients/python/

http://stackoverflow.com/questions/24637763/wrapping-mqtt-data-in-ssl-certificate-while-sending-it-to-mqtt-broker


-----

## Install Mosquitto

The Raspbian repo version of Mosquitto is a bit old and may have bad
support for SSL `Mosquitto version 1.3.4`. Add Mosquittos apt repositories 
for `Mosquitto version 1.4.11`.

```bash
# add mosquitto apt repositories for Mosquitto version 1.4.11
wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
sudo apt-key add mosquitto-repo.gpg.key
cd /etc/apt/sources.list.d/
sudo wget http://repo.mosquitto.org/debian/mosquitto-jessie.list

# install Mosquitto broker, cli clients and paho mqtt python client
sudo apt-get update 
sudo apt-get install mosquitto mosquitto-clients 
sudo pip install -U paho-mqtt
sudo pip3 install -U paho-mqtt
```

## Configure 

- Default config: `/etc/mosquitto/mosquitto.conf`
- My extensions: `/etc/mosquitto/conf.d/mosquitto_ssl_tls.conf`

```bash
sudo systemctl restart mosquitto.service
sudo systemctl status mosquitto.service
```

-----

## Test Pub-Sub via Mosquitto CLI

```bash
mosquitto_sub -d -t hello/world &
mosquitto_pub -d -t hello/world -m "Hello from publisher!"
```

## Test Pub-Sub via Paho-MQTT Python Client

```bash
mosquitto_sub -d -t ledStatus &
```

```python
import paho.mqtt.publish as publish
import time
print("Sending 0...")
publish.single("ledStatus", "0", hostname="localhost")
time.sleep(1)
print("Sending 1...")
publish.single("ledStatus", "1", hostname="localhost")
```


------

## Secure MQTT - Configuring SSL/TLS


### Configuration

- Extend config with `/etc/mosquitto/conf.d/mosquitto_tls_ssl.conf`.

```
# standard port for secure mqtt
listener 8883
require_certificate true

# certs for tls/ssl
cafile /etc/mosquitto/ca_certificates/ca.crt
certfile /etc/mosquitto/certs/raspiflow.crt
keyfile /etc/mosquitto/certs/raspiflow.key
```

https://mosquitto.org/man/mosquitto-conf-5.html

Restart broker service to enable config.
```bash
sudo systemctl restart mosquitto.service
sudo systemctl status mosquitto.service
```

### Generate Certs

https://mosquitto.org/man/mosquitto-tls-7.html

Setup a CA and generate certs for server and clients. Avoid using identical 
parameters for server and client csr (this can create problems apparently...).


```bash
mkdir -p certs/ca
cd certs

DURATION=365

## ca certs
openssl req -new -x509 -days $DURATION -extensions v3_ca -keyout ca.key -out ca/ca.crt

## server certs

#openssl genrsa -des3 -out server.key 2048			# server key encrypted, TROUBLE LOADING! Passphrase protected.
openssl genrsa -out server.key 2048 				# server key non-encrypted
openssl req -out server.csr -key server.key -new	# server cert sign requst

# sign csr with ca using the ca key and get a server cert
openssl x509 -req -in server.csr -CA ca/ca.crt -CAkey ca/ca.key \
	-CAcreateserial -out server.crt -days $DURATION


## client certs
#openssl genrsa -des3 -out client.key 2048			# client key encrytped
openssl genrsa -out client.key 2048					# client key unencrytped
openssl req -out client.csr -key client.key -new	# client cert sign request

# sign csr with ca using the ca key and get a server cert
openssl x509 -req -in client.csr -CA ca/ca.crt -CAkey ca/ca.key \
	-CAcreateserial -out client.crt -days $DURATION
```

### Copy Certs into place

```bash
sudo cp ca/ca.crt /etc/mosquitto/ca_certificates/
sudo cp server.crt /etc/mosquitto/certs/raspiflow.crt
sudo cp server.key /etc/mosquitto/certs/raspiflow.key
```
 
## Test Secure MQTT 

```bash
mosquitto_sub --cafile ca/ca.crt --cert client.crt --key client.key \
	-h raspiflow -p 8883 -d -t hello/world 

mosquitto_pub --cafile ca/ca.crt --cert client.crt --key client.key \
	-h raspiflow -p 8883 -d -t hello/world \
	-m "Hello TLS/SSL!"
```

- Promted for passphrase for *client.key* if encrypted.


## Test Sequre MQTT with Python

**Subscribe**
```python 
from __future__ import print_function
import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, msg):
    print(msg.topic, " ", str(msg.payload))

client = mqtt.Client()
client.tls_set("ca.crt", certfile="client.crt", keyfile="client.key")
client.on_message = on_message
client.connect("raspiflow", 8883, 60)

topic = "ledStatus"
client.subscribe(topic)
client.loop_forever()
```

**Publish**
```python
import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.tls_set("ca.crt", certfile="client.crt", keyfile="client.key")
client.connect("raspiflow", 8883, 60)

topic = "ledStatus"
print("Sending 0...")
client.publish(topic, "0")
time.sleep(1)
print("Sending 1...")
client.publish(topic, "1")
```

----

## Auth

https://mosquitto.org/man/mosquitto_passwd-1.html

```
allow_anonymous false
password_file /etc/mosquitto/passwd
```

```bash
# Add a user to a new password file:
mosquitto_passwd -c /etc/mosquitto/passwd ral

# Delete a user from a password file
mosquitto_passwd -D /etc/mosquitto/passwd ral
```

-----

## MQTT Security


### Authentication

**User/Password Authentication**
- On the application level the MQTT protocol provides username and password for authentication.
- The MQTT protocol itself provides username and password fields in the CONNECT message.
- To guarantee a completely secure transmission of username and password we must use transport encryption, TLS.

http://www.hivemq.com/blog/mqtt-security-fundamentals-authentication-username-password

**Advanced Authentication:**
- Every MQTT client has a unique **client identifier**.
- X.509 **client certificate**. Broker can use the information in the certificate for application layer authentication after the TLS handshake already succeeded.

http://www.hivemq.com/blog/mqtt-security-fundamentals-advanced-authentication-mechanisms


### Authorization

- Controling access to resources.
- Without proper authorization each authenticated client can publish and subscribe to all kinds of topics. 

Two most common models:
1. **ACL**		Access Control List
2. **RBAC**		Role Based Access Control

In order to restrict a client to publish or subscribe only to topics it is authorized to, it is necessary to implement topic permissions on the broker side. 
A topic permission could for example look like the following:
- Allowed topic (exact topic or wild card topic)
- Allowed operation (publish, subscribe, both)
- Allowed quality of service level (0, 1, 2, all)

http://www.hivemq.com/blog/mqtt-security-fundamentals-authorization/


### TLS/SSL

- MQTT relies on TCP as transport protocol, which means by default the connection does not use an encrypted communication. 
- *Port 8883* is standardized for a secured MQTT connection, *MQTT over TLS*.
- Communication overhead of the *TLS Handshake* can be significant if the MQTT client connections are expected to be short-lived. 
- Using long-living TCP connections with MQTT, the TLS overhead, especially the TLS Handshake overhead may be negligible.
- *TLS Session Resumption* in the previous paragraphs. In a nutshell, TLS session resumption techniques allow to reuse an already negotiated TLS session after reconnecting to the server, so the client and server don’t need to do the full TLS handshake again.

http://www.hivemq.com/blog/mqtt-security-fundamentals-tls-ssl


### X509

**TLS and X509 certificates**
- **Server Certificates**: In order to use TLS, the server needs a public / private key pair. When the TLS handshake takes place, clients need to validate the X509 certificate of the server, which also contains the public key of the server, before a secure connection can be established.
- **Client Certificates**: Clients can also have a unique public / private key pair which can be used in the TLS handshake. The client sends its certificate (which includes the public key of the client) as part of the TLS handshake after the server certificate is validated. 
- **The server is then able to verify the identity of the client and can abort the handshake if the verification of the client certificate fails.**

**Client Certificates Advantages:**
- Verification of the identity of MQTT clients
- Authentication of MQTT clients at transport level
- Lock out invalid MQTT clients before MQTT CONNECT messages are sent

**Before using client certificates, make sure you have a solid and secure certificate provisioning process.**
- Can provide the certificate e.g. as part of your device firmware update process.
- Manage the lifecycle of the client certificates. In case you already have deployed a PKI (Public-Key-Infrastructure), this should not be a problem. 

**You also need a certificate revocation mechanism.**
- *Certificate Revocation Lists* (CRLs). CRLs are a good way if you have only a few certificates deployed to MQTT clients but can be big headache if you are dealing with thousands or hundreds of thousands of certificates.
- Online Certificate Status Protocol (OCSP)

http://www.hivemq.com/blog/mqtt-security-fundamentals-x509-client-certificate-authentication


### OAuth2

**OAuth 2.0 is an authorization framework, that allows a third party to access a resource owned by a resource owner without giving unencrypted credentials to the third party.**

- Connect to an MQTT broker with an Access Token
- Publish/Subscribe with an Access Token

**Sharing resources**
If the client has successfully retrieved an access token, it can send it to the broker in the CONNECT message using the password field. 
When the broker gets the token it can do different types of validations:
- Check the *validity of the signature from the token*.
- Check if the *expiration date of the token* has already passed.
- Check on the *authorization server if the token was revoked*.

http://www.hivemq.com/blog/mqtt-security-fundamentals-oauth-2-0-mqtt


### Payload Encryption

- Since **MQTT payloads are always binary**, it’s *not needed to encode the encrypted message to an textual representation*, 
  like base64. This is important if you need to save additional bandwidth.

- **End-to-End (E2E) encryption** is broker implementation independent and can be applied to any topic by any MQTT client.
- **Client-to-Broker**

**Asymmetric encryption**
- Public key for encrypting data and one private key for decrypting data.
- Perfect if you only have a few trusted subscribers (which have access to the private key) and there are many publishers (which are possibly untrusted).
- Best practice that each MQTT topic gets its own public / private key pair.

**Symmetric Encryption**
- encrypt and decrypt a message with the same key (which may be a password).
- recommended that each MQTT topic gets its own key (password)

http://www.hivemq.com/blog/mqtt-security-fundamentals-payload-encryption


### Data Integrity

**With data integrity checks you make sure that no third party modified any contents of your MQTT messages. **

**Methods:**
- **Checksums**: Checksums can get altered with the MQTT packet, since the attacker only needs to know the checksum algorithm.
- **MACs**: Message Authentication Code Algorithms (like HMAC) are typically very fast compared to digital signatures and provide good security if the shared secret key was exchanged securely prior to the MQTT communication. Only senders which know the secret key can create a valid stamp. The disadvantage is, that all clients who are aware of the secret key can sign and verify, since the same key is involved for both processes.
- **Digital Signatures**: The sender signs the message with its private key and the receiver validates the stamp (signature) with the public key of the sending client. Challanges are: provisioning and revocation of public/private keys and that in Publish/Subscribe systems the  receiver of a message typically is not aware of the identity of the sender. Used together with *Authorization* this approach can work good, where only a specific client can publish to a specific topic.

http://www.hivemq.com/blog/mqtt-security-fundamentals-mqtt-message-data-integrity


### MQTT Security Fundamentals

Security on different levels:
1. Infrastructure
2. Operating System
3. MQTT Broker

**MQTT Broker:**
- Authentication and Authorization
- TLS
- Throttling - throttling MQTT clients can add additional protection for overloading MQTT brokers.
- Message Size - MQTT defines a maximum message size of 256MB. **decrease the maximum allowed message size.**

http://www.hivemq.com/blog/mqtt-security-fundamentals-securing-mqtt-systems


