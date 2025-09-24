### action test ###

# MQTT setting
import rtde_io
import rtde_receive
import paho.mqtt.client as mqtt
import json
import time
from rtde_control import RTDEControlInterface as RTDEControl

robot_ip = "192.168.56.101"
rtde_c = RTDEControl(robot_ip, RTDEControl.FLAG_CUSTOM_SCRIPT)
rtde_io_ = rtde_io.RTDEIOInterface(robot_ip)
rtde_receive_ = rtde_receive.RTDEReceiveInterface(robot_ip)
port1 = 0
# rob = urx.Robot(robot_ip)


# def urx_io_comm_on_off(robot_ip, port):
#     rob.set_digital_out(port, True)
#     time.sleep(1)
#     rob.set_digital_out(port, False)
#     # rob.close()
#     # time.sleep(1)

multiple_coordinates = [
    [0.444, -0.135, 0.20, -0.151, 3.27, 0.64],
    [-0.243, -0.235, 0.30, -0.101, 3.22, 0.14],
    [-0.343, -0.335, 0.35, -0.071, 3.12, 0.34],
    [-0.283, -0.285, 0.27, -0.091, 3.17, 0.24]
]

print("0 : Move pos1")
rtde_c.moveL(multiple_coordinates[0])
# time.sleep(1)
# rtde_c.moveL([-0.111, -0.222, -0.333, -0.123, 3.12, 0.34])

print("1 : port1 False")
# urx_io_comm_on_off(robot_ip, 1)
rtde_io_.setStandardDigitalOut(port1, False)
rtde_io_.setToolDigitalOut(port1, False)
time.sleep(1)

print("2 : Move pos2")
rtde_c.moveL(multiple_coordinates[1])
# time.sleep(1)

print("3 : port1 True")
# urx_io_comm_on_off(robot_ip, 3)
rtde_io_.setStandardDigitalOut(port1, True)
rtde_io_.setToolDigitalOut(port1, True)
time.sleep(1)

print("4 : Move pos3")
rtde_c.moveL(multiple_coordinates[2])


print("finished")
# rob.close()
# rtde_c.disconnect()



#########################################################

def robot_control_no_speed(coordinate):
    rtde_c.moveL(coordinate)
    print("\nMove robot to " + str(coordinate) + "\n")
    # send_urscript_to_robot(robot_ip, port, io_command)
    # print("Send I/O signal\n")


def open_io_socket():
    global io_socket
    io_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    io_socket.connect((robot_ip, port))

def close_io_socket():
    global io_socket
    if io_socket:
        io_socket.close()
        io_socket = None

# To send I/O signal
# def set_all_digital_outputs(ip, port, io_list, state):
def set_all_digital_outputs():
    global io_socket
    
    
    ### Before revise seperating threading
    # for i in io_list:
    #     command = f"set_digital_out({i}, {state})\n"
    #     io_socket.sendall(command.encode('utf-8'))
    #     time.sleep(0.5)

    # if io_queue:
    #     io_port = io_queue.pop(0)
    #     command = f"set_digital_out({io_port}, {state})\n"
    #     io_socket.sendall(command.encode('utf-8'))
    #     time.sleep(0.5)
    #     state = not state ### For toggle io_state
    #     print(f"I/O port {io_port} set to {'ON' if io_state else 'OFF'}" + "\n--------------------------------")
    #     time.sleep(1)

    ### After revised
    global move_completed_event, io_completed_event
    state = True
    while True:
        move_completed_event.wait() # wait for move to complete
        move_completed_event.clear() # reset for next cycle
        if io_queue:
            if not io_socket:
                open_io_socket()
            
            io_port = io_queue.pop(0)
            for i in io_port:
                command = f"set_digital_out({i}, {state})\n"
            io_socket.sendall(command.encode('utf-8'))
            time.sleep(0.5)
            state = not state ### For toggle io_state
            print(f"I/O port {io_port} set to {'ON' if state else 'OFF'}" + "\n--------------------------------")
            time.sleep(1)
            io_completed_event.set() # signal that i/o is complete
            close_io_socket()
            

# thread-safe queue for movement commands
command_queue = []
# command_queue에서 계속 coordinate 받아서 seperate daemon thread에서 robot control 실시.
def process_robot_commands():
    global move_completed_event, io_completed_event
    ### Before revise seperating threading
    # io_state = True
    while True:
        if command_queue:
            coordinate = command_queue.pop(0)
            robot_control_no_speed(coordinate)

            ### Wait until the robot reaches target position
            # while not is_at_position(coordinate):
            #     time.sleep(0.1)
            time.sleep(5)

            ### After revise separating threading
            print("Move to position completed\n")
            move_completed_event.set() # signal that move is complete
            io_completed_event.wait() # wait for i/o to complete
            io_completed_event.clear() # reset for next cycle
        
            ### I/O communication
            ### Before revise separating threading
            # if io_queue:
            #     io_port = io_queue.pop(0)
            #     set_all_digital_outputs(robot_ip, port, io_port, io_state)
            #     io_state = not io_state ### For toggle io_state
            #     print(f"I/O port {io_port} set to {'ON' if io_state else 'OFF'}" + "\n--------------------------------")
            #     time.sleep(1)
        else: # because initially command queue is empty
            time.sleep(0.1)
    # close_io_socket()

# Start the thread working

