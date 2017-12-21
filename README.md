
# Mosquitto Gateway Forwarding Topics to AWS IoT


## Prerequsites

- Assume the *Mosquitto Broker* is configured, up and running. 
- Assume Mosquitto and AWS IoT certificates and configuration is all setup. 
- See [Mosquitto README](README.mosquitto.md) and [AWS IoT README](README.awsiot.md).

The Datashipper `mosquitto_awsiot_datashipper.py` and Publisher `mosquitto_awsiot_publisher.py` rely
on the following python packages:
```bash
sudo pip install -U paho-mqtt
sudo pip install -U AWSIoTPythonSDK
```

## Example Usage

- Datashipper that forwarding topic `events/#` to AWS IoT.
- An example publisher that publish to topic `events/test` by default.

```bash
python mosquitto_awsiot_datashipper.py &
python mosquitto_awsiot_publisher.py 
```

## Proxy
MQTT is not compatible with http/https-proxy (?), but tsocks4/5 works fine.

If tsocks is set up on your machine you can run
```bash
tsocks python mosquitto_awsiot_datashipper.py
```

Can probably also be implemented using SocksiPy (?), something like this:
```python
import socks
import socket
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 8080)
socket.socket = socks.socksocket
```
