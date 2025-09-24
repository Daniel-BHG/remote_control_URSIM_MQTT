import argparse
import logging
import sys

sys.path.append("..")
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import rtde.csv_writer as csv_writer
import rtde.csv_binary_writer as csv_binary_writer

import json
import paho.mqtt.client as mqtt

##### convert data_object to dict type ##### 
def data_object_to_dict(data_object):
    return data_object.__dict__

# MQTT communication
client = mqtt.Client()
client.connect('175.106.99.82', 1883, 60)  # Replace 'broker_address' with your broker's address
client.loop_start()  # Start the network loop in a separate thread

# parameters
parser = argparse.ArgumentParser()
parser.add_argument(
    "--host", default="192.168.56.101", help="name of host to connect to (localhost)"
)
parser.add_argument("--port", type=int, default=30004, help="port number (30004)")
parser.add_argument(
    "--samples", type=int, default=0, help="number of samples to record"
)
parser.add_argument(
    "--frequency", type=int, default=10, help="the sampling frequency in Herz"
)
parser.add_argument(
    "--config",
    default="record_configuration.xml",
    help="data configuration file to use (record_configuration.xml)",
)
parser.add_argument(
    "--output",
    default="robot_data.csv",
    help="data output file to write to (robot_data.csv)",
)
parser.add_argument("--verbose", help="increase output verbosity", action="store_true")
parser.add_argument(
    "--buffered",
    help="Use buffered receive which doesn't skip data",
    action="store_true",
)
parser.add_argument(
    "--binary", help="save the data in binary format", action="store_true"
)
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.INFO)

conf = rtde_config.ConfigFile(args.config)
output_names, output_types = conf.get_recipe("out")

con = rtde.RTDE(args.host, args.port)
con.connect()

# get controller version
con.get_controller_version()

# setup recipes
if not con.send_output_setup(output_names, output_types, frequency=args.frequency):
    logging.error("Unable to configure output")
    sys.exit()

# start data synchronization
if not con.send_start():
    logging.error("Unable to start synchronization")
    sys.exit()

writeModes = "wb" if args.binary else "w"
with open(args.output, writeModes) as csvfile:
    writer = None

    if args.binary: # whether to write data in binary type
        writer = csv_binary_writer.CSVBinaryWriter(csvfile, output_names, output_types)
    else: # write data in text type
        writer = csv_writer.CSVWriter(csvfile, output_names, output_types)

    writer.writeheader()

    i = 1
    keep_running = True
    while keep_running:

        if i % args.frequency == 0:
            if args.samples > 0:
                sys.stdout.write("\r")
                print(str(args.samples))
                sys.stdout.write("{:.2%} done.".format(float(i) / float(args.samples)))
                sys.stdout.flush()
            else: # frequncy != 0 이므로 else로
                sys.stdout.write("\r")
                sys.stdout.write("{:3d} samples.".format(i))
                sys.stdout.flush()
        if args.samples > 0 and i >= args.samples:
            keep_running = False
        try:
            if args.buffered: # receive the "buffered" data
                state = con.receive_buffered(args.binary)
                print(str(state))
            
            ### 밑의 else와 if문을 반복하며 저장하므로 자세히 보기 ###
            else: # receive none buffered data.               
                ### 여기서 state 뭘 어떻게 받는지 중요
                # received state -> <rtde.serialize.DataObject object at 0x000001ECD3051F10>
                # type of state -> <class 'rtde.serialize.DataObject'>
                state = con.receive(args.binary)

            ### State writing part
            if state is not None:
                ### convert data type to dict
                ### state_dict has total keys & values of all robot's state
                state_dict = data_object_to_dict(state) 
                ### state_dict_target_q is only get target_q component frome state_dict
                state_dict_target_q = state_dict.get('target_q', None) 

                print(state_dict.get('target_q', None), "\n")
                
                state_json = json.dumps(state_dict) # convert state_dict to json type
                state_json_target_q = json.dumps(state_dict_target_q) # convert state_dict_target_q to json type

                ### [Full data = state_json] vs. [Target_q data = state_json_target_q]
                # client.publish("robot_status", state_json, 1) ## publish full robot state data
                client.publish("send_robot_status", state_json_target_q, 1) ## publish Target_q data

                writer.writerow(state) # write to CSV file
                i += 1

        except KeyboardInterrupt:
            keep_running = False
        except rtde.RTDEException:
            con.disconnect()
            sys.exit()


sys.stdout.write("\rComplete!            \n")

client.loop_stop()  # Stop the network loop
client.disconnect()  # Disconnect the client

con.send_pause()
con.disconnect()
