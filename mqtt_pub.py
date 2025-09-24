### MQTT_Publish ###
### Remember this as pub.py ###

import paho.mqtt.client as mqtt
import json
import subprocess
import time

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_publish(client, userdata, mid):
    print("on pub message = ", mid)

''' Sending data part '''
### Single coordinate
data1 = json.dumps([-0.143, -0.135, 0.20, -0.151, 3.27, 0.64]) # sent data by json
data2 = json.dumps([-0.243, -0.235, 0.30, -0.101, 3.22, 0.14])

### Multiple coordinate at once
multiple_coordinates = [
    [0.444, -0.135, 0.20, -0.151, 3.27, 0.64],
    [-0.243, -0.235, 0.30, -0.101, 3.22, 0.14],
    [-0.343, -0.335, 0.35, -0.071, 3.12, 0.34],
    [-0.483, -0.485, 0.47, 0.101, 3.07, 0.44]
]
data_multiple_coor = json.dumps(multiple_coordinates)

### I/O communication
io_outputs = [[0], [2], [5], [7]]
data_io_outputs = json.dumps(io_outputs)

''' Module part '''
# Generate new client
client = mqtt.Client()
client.on_connect = on_connect 
client.on_publish = on_publish 
# client.on_message = on_message

record_process = subprocess.Popen(['python', 'record.py'])
time.sleep(1)

client.connect('175.106.99.82', 1883)
client.loop_start()

''' Publish part '''
### Single moveL command
# client.publish("target_command", data1, 1)
# time.sleep(3)
# client.publish("target_command", data2, 1)
# time.sleep(3)

### Multiple moveL command
client.publish("io_communication", data_io_outputs, 1)
client.publish("target_command", data_multiple_coor, 1)

### Enough time is needed due to record_process
time.sleep(20)
record_process.terminate()
record_process.wait()
client.loop_stop()
