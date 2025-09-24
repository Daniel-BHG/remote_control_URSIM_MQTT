import socket
import time
# import ur_rtde
import urx
import time
from rtde_control import RTDEControlInterface as RTDEControl

robot_ip = "192.168.56.101"
port = 30002 # URScript port that will not interfere primary port


''' ##### Single I/O command ##### '''
# def send_urscript_to_robot(ip, port, script):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.connect((ip, port))
#         sock.sendall(script.encode('utf-8'))

# # URScript command to set a digital output
# io_command = "set_digital_out(1, True)\n"  # Turn on digital output 1

# send_urscript_to_robot(robot_ip, port, io_command)


''' ##### Multiple I/O command ##### '''
# To send I/O signal
'''
number_of_outputs = [0,2,5,7]
def set_all_digital_outputs(ip, port, state):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        for i in number_of_outputs:
            command = f"set_digital_out({i}, {state})\n"
            sock.sendall(command.encode('utf-8'))
            time.sleep(0.5)

set_all_digital_outputs(robot_ip, port, True)
time.sleep(0.1)
set_all_digital_outputs(robot_ip, port, False)
'''

### import ur_rtde 
# rtde_c = ur_rtde.RTDEControlInterface(robot_ip)
# rtde_c.sendScript("set_digital_out(0, True)")
# rtde_c.disconnect()

### import urx
rob = urx.Robot(robot_ip)
rob.set_digital_out(2, True)
# time.sleep(1)
rob.set_digital_out(2, False)
rob.close()