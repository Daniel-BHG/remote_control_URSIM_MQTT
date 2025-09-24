import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_publish(client, userdata, mid):
    print("on pub message = ", mid)

data1 = json.dumps([-0.143, -0.135, 0.20, -0.151, 3.27, 0.64]) # sent data by json
data2 = json.dumps([-0.243, -0.235, 0.30, -0.101, 3.22, 0.14])

client = mqtt.Client()
client.on_connect = on_connect # connect to broker
client.on_publish = on_publish # publish message

client.connect('223.130.136.168', 1883) # 1.241.238.220 : 13028
client.loop_start()

time.sleep(3)
client.publish("target_command", data1, 1)
time.sleep(3)
client.publish("target_command", data2, 1)

client.loop_stop()
client.disconnect()