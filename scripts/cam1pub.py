#!/usr/bin/python3

import rospy
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import numpy as np
import cv2
import socket
import time
import struct
import threading
import yaml


config_file_path = sys.argv[1]
config = ""

with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)

topic_name = config["topics"]["topic1_name"]

PORT = 9050
BUFFER_SIZE = 8 * 1000
RESTART_THRESHOLD = 2  # in seconds
MAX_PACKET_SIZE = 65450  # Maximum size for a UDP packet
FPS=7
__udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
__udp_server_socket.bind(('0.0.0.0', PORT))
address =None# ('192.168.0.77',9051)
last_received_time = time.time()
frame_count=0
dim = (1080,720)



def callback(image_msg):
    """This function is called to handle the subscribed messages

    Args:
        image_msg (Image): message type Image from sensor_msgs
    """
    try:
        cv_image = bridge.imgmsg_to_cv2(image_msg,"bgr8")
#        cv2.imshow('ROS Image Subscriber', cv_image)
        #cv2.imwrite('ros_image1.jpg',cv_image)
        if address is not None:
            _, img_bytes = cv2.imencode('.jpg', cv_image) #resize

            img_byte_array = np.array(img_bytes).tobytes()
            
            # Split the data into smaller chunks and send them separately
            totalstepsrequired=0
            for i in range(0, len(img_byte_array), MAX_PACKET_SIZE):
                totalstepsrequired=totalstepsrequired+1

            count=0
            for i in range(0, len(img_byte_array), MAX_PACKET_SIZE):
                chunk = img_byte_array[i:i + MAX_PACKET_SIZE]
                chunkwithcunkId = struct.pack('i', count)+struct.pack('i', totalstepsrequired)  + chunk #struct.pack('i', arrlen)+
                __udp_server_socket.sendto(chunkwithcunkId, address)

#                print("image data sent")
                time.sleep(1 / 1000)
                count= count+1


        cv2.waitKey(10)
    except CvBridgeError as error:
        print(error)
        t1.join()

def threadcheckdevices():
    global address
    global __udp_server_socket
    while(True):
        try:   
            try:
                __udp_server_socket.settimeout(0.05)
                _, new_address = __udp_server_socket.recvfrom(BUFFER_SIZE)
                if new_address != address:
                    address = new_address
                    (CLIENT_IP,port) = address
                    print(f'New client {address} got connected (usb_cam1)')
                last_received_time = time.time()
            except socket.timeout:
                continue
            except Exception as e:
                print(e)
                __udp_server_socket.close()
                __udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                __udp_server_socket.bind(('0.0.0.0', PORT))
                address = None
                continue
        except KeyboardInterrupt:
            print("Program terminated by user from main")
            is_running = False
            break

if __name__=="__main__":
    
    t1 = threading.Thread(target=threadcheckdevices)
    t1.start()
    bridge = CvBridge()
    rospy.init_node("image_subscriber", anonymous=True)
    print(f"Subscribe images from topic {topic_name} ...")

    image_subcriber = rospy.Subscriber(topic_name, Image, callback)

    try:
        # spin() simply keeps python from exiting until this node is stopped
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down!")
        t1.join()

