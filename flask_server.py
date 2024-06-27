#!/usr/bin/python3

from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# GLOBAL PROCESSES
BRINGUP = None
STARTTCP = None
USBCAM = None

def kill(pid):
    os.kill(pid,signal.SIGTERM ) #SIGKILL , SIGTERM

def start_proc(command: str, package_name : str, launch_file: str) -> subprocess:
    proc = subprocess.Popen([
        command, 
        package_name,
        launch_file,
    ])
    return proc

@app.route('/save_rosbag', methods=['POST'])
def save_rosbag():
    name = request.form.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    return jsonify({'message': f'Name received: {name}'}), 200

@app.route('/rosbag_play', methods=['POST'])
def rosbag_play():
    file_name = request.form.get('filename')
    speed = request.form.get('speed')
    
    if not file_name:
        return jsonify({'error': 'Filename  is required'}), 400
    if not speed:
        return jsonify({'error': 'Speed is required'}), 400

    return jsonify({'message': f'Name received:'}), 200

@app.route('/start_tcp', methods=['GET'])
def start_tcp():
    global STARTTCP 
    if STARTTCP != None:
        kill(STARTTCP.pid)
        STARTTCP = start_proc("roslaunch","ros_tcp_endpoint","endpoint.launch")
    else:
        STARTTCP = start_proc("roslaunch","ros_tcp_endpoint","endpoint.launch")
    return jsonify({'message': f'Starting TCP'}), 200

@app.route('/usb_cam', methods=['GET'])
def usb_cam():
    global USBCAM 
    if USBCAM != None:
        kill(USBCAM.pid)
        USBCAM = start_proc("roslaunch","usb_cam","2_usb_cam.launch")
    else:
        USBCAM = start_proc("roslaunch","usb_cam","2_usb_cam.launch")
    return jsonify({'message': f'Starting USB Cam'}), 200

@app.route('/robot_bringup', methods=['GET'])
def robot_bringup():
    global BRINGUP 
    if BRINGUP != None:
        kill(BRINGUP.pid)
        BRINGUP = start_proc("roslaunch","tortoisebot_firmware","bringup.launch")
    else:
        BRINGUP = start_proc("roslaunch","tortoisebot_firmware","bringup.launch")
    return jsonify({'message': f'Starting Robot Bringup'}), 200

@app.route('/start_rosbag_record', methods=['GET'])
def start_rosbag_record():
    return jsonify({'message': f'Starting RosBag Record'}), 200

@app.route('/rosbag_list', methods=['GET'])
def rosbag_list():
    return jsonify({'message': f'Starting RosBag Record'}), 200

if __name__ == '__main__':
    app.run(debug=True)

