#!/usr/bin/python3

from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

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
    return jsonify({'message': f'Starting TCP'}), 200

@app.route('/usb_cam', methods=['GET'])
def usb_cam():
    return jsonify({'message': f'Starting USB Cam'}), 200

@app.route('/robot_bringup', methods=['GET'])
def robot_bringup():
    return jsonify({'message': f'Starting Robot Bringup'}), 200

@app.route('/start_rosbag_record', methods=['GET'])
def start_rosbag_record():
    return jsonify({'message': f'Starting RosBag Record'}), 200

@app.route('/rosbag_list', methods=['GET'])
def rosbag_list():
    return jsonify({'message': f'Starting RosBag Record'}), 200

if __name__ == '__main__':
    app.run(debug=True)

