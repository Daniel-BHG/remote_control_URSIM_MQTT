### MQTT_Subscribe ###
### Remember this as sub.py ###

### MQTT setting
import paho.mqtt.client as mqtt
import json
import threading
import time
import rtde_io
import rtde_receive
from rtde_control import RTDEControlInterface as RTDEControl

robot_ip = "192.168.56.101"
rtde_c = RTDEControl(robot_ip, RTDEControl.FLAG_CUSTOM_SCRIPT)
rtde_io_ = rtde_io.RTDEIOInterface(robot_ip)
rtde_receive_ = rtde_receive.RTDEReceiveInterface(robot_ip)

io_queue = []
command_queue = []

### MoveL and IO communication process function
def process_robot_commands():
    io_state = True
    while True:
        ### Move robot
        if command_queue:
            coordinate = command_queue.pop(0)
            robot_control_no_speed(coordinate)
            print("Move to position completed\n")

            ### I/O communication
            if io_queue:
                for io_ports in io_queue:
                    for io_port in io_ports: ### convert list to int
                        ### Digital output I/O
                        rtde_io_.setStandardDigitalOut(io_port, io_state)
                        print(f"Digital Output port {io_port} = {io_state}")
 
            ### Tool Digital output I/O
            rtde_io_.setToolDigitalOut(0, io_state)
            print(f"Tool digital output port 0 = {io_state}\n")
            io_state = not io_state
            time.sleep(0.1)

### Start the thread working
command_thread_move = threading.Thread(target=process_robot_commands, daemon=True)
command_thread_move.start()

### The callback for when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    ### convert received moveL coordinate to list
    if msg.topic == "target_command":
        print("\nTopic : " + msg.topic)
        coordinate_list = json.loads(msg.payload.decode('utf-8'))
        ### check if the received coordinate is list type
        if isinstance(coordinate_list, list):
            ### Add command to command_queue for threaded control
            command_queue.extend(coordinate_list) 
        else:
            print("Received payload is not a list type: ", coordinate_list)

    ### Add queue of published IO port
    if msg.topic == "io_communication":
        print("\nTopic : " + msg.topic)
        io_list = json.loads(msg.payload.decode('utf-8'))
        print(str(io_list))
        if isinstance(io_list, list):
            io_queue.extend(io_list)
        else:
            print("Received payload is not a list type: ", io_list)

        ### Receive current robot status
    if msg.topic == "send_robot_status":
        target_q_data = json.loads(msg.payload.decode('utf-8'))
        # print("Received 'target_q' data:\n", target_q_data, "\n")

### MoveL command
def robot_control_no_speed(coordinate):
    print("Start to move robot to " + str(coordinate) + "\n")
    rtde_c.moveL(coordinate)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed " + str(mid) + " " + str(granted_qos))

### Generate new client
client = mqtt.Client()

### target_command -> MoveL coordinate from publish.py
### io_communication -> IO port from publish.py
### send_robot_status -> current robot state from record.py
client.on_connect = lambda c, u, f, rc: c.subscribe([("target_command", 1), ("io_communication", 1), ("send_robot_status", 1)])
client.on_subscribe = on_subscribe
client.on_message = on_message

client.connect('175.106.99.82', 1883)
client.loop_forever()
