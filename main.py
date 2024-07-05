from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
import subprocess
import os
import signal
import uvicorn

app = FastAPI()

# GLOBAL PROCESSES
BRINGUP = None
STARTTCP = None
USBCAM = None
ROSBAG = None
ROSBAG_RECORD = None

def kill(pid):
    os.kill(pid, signal.SIGTERM)  # SIGKILL , SIGTERM

def start_proc(command: str, package_name: str, launch_file: str) -> subprocess.Popen:
    command = f"source /opt/ros/noetic/setup.bash && source /home/tortoisebot/ros1_ws/devel/setup.bash && {command} {package_name} {launch_file}"
    proc = subprocess.Popen([
        command
    ],
    shell=True,
    executable="/bin/bash")
    return proc

def check_or_create_bags_directory():
    directory = "bags"
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory for Bags already '{directory}' created.")
    else:
        print(f"Directory for Bags already '{directory}' already exists.")

def kill_roslaunch_processes():
    try:
        ps_output = subprocess.check_output(['ps', 'aux'])
        ps_output = ps_output.decode('utf-8')
        processes = [line for line in ps_output.split('\n') if 'roslaunch' in line]
        for process in processes:
            if process:
                pid = int(process.split()[1])
                subprocess.run(['kill', '-9', str(pid)])
                print(f"Killed process with PID {pid}")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


@app.post("/rosbag_play")
async def rosbag_play(file_name: str = Form(...), speed: str = Form(...)):
    if not file_name:
        return JSONResponse(content={'error': 'Filename is required'}, status_code=400)
    if not speed:
        return JSONResponse(content={'error': 'Speed is required'}, status_code=400)
    return JSONResponse(content={'message': 'Name received:'}, status_code=200)

@app.get("/start_tcp")
async def start_tcp():
    global STARTTCP
    if STARTTCP is not None:
        kill(STARTTCP.pid)
        STARTTCP = start_proc("roslaunch", "ros_tcp_endpoint", "endpoint.launch")
    else:
        STARTTCP = start_proc("roslaunch", "ros_tcp_endpoint", "endpoint.launch")
    return JSONResponse(content={'message': 'Starting TCP'}, status_code=200)

@app.get("/stop_tcp")
async def stop_tcp():
    global STARTTCP
    kill(STARTTCP.pid)
    return JSONResponse(content={'message': 'Killed TCP'}, status_code=200)


@app.get("/usb_cam")
async def usb_cam():
    global USBCAM
    if USBCAM is not None:
        kill(USBCAM.pid)
        USBCAM = start_proc("roslaunch", "usb_cam", "2_usb_cam.launch")
    else:
        USBCAM = start_proc("roslaunch", "usb_cam", "2_usb_cam.launch")
    return JSONResponse(content={'message': 'Starting USB Cam'}, status_code=200)


@app.get("/stop_usb_cam")
async def stop_usb_cam():
    global USBCAM
    if USBCAM is not None:
        kill(USBCAM.pid)
    else:
        kill(USBCAM.pid)
    return JSONResponse(content={'message': 'Killing USB Cam'}, status_code=200)

@app.get("/robot_bringup")
async def robot_bringup():
    global BRINGUP
    if BRINGUP is not None:
        kill(BRINGUP.pid)
        BRINGUP = start_proc("roslaunch", "tortoisebot_firmware", "bringup.launch")

    else:
        BRINGUP = start_proc("roslaunch", "tortoisebot_firmware", "bringup.launch")
        #kill(BRINGUP.pid)
        #BRINGUP = start_proc("roslaunch", "tortoisebot_firmware", "bringup.launch")
    return JSONResponse(content={'message': 'Starting Robot Bringup'}, status_code=200)

@app.get("/stop_bringup")
async def stop_bringup():
    global BRINGUP
    if BRINGUP is not None:
        kill_roslaunch_processes()
        kill(BRINGUP.pid)
        BRINGUP = None
    else:
        #kill(BRINGUP.pid)
        pass
    return JSONResponse(content={'message': 'Stopped Robot Bringup'}, status_code=200)

@app.post("/start_rosbag_record")
async def start_rosbag_record(file_name: str = Form(...)):
    check_or_create_bags_directory()
    global ROSBAG_RECORD
    if not file_name:
        return JSONResponse(content={'error': 'Filename is required'}, status_code=400)
    if ROSBAG_RECORD is not None:
        kill(ROSBAG_RECORD.pid)
        ROSBAG_RECORD = subprocess.Popen([
            f"source /opt/ros/noetic/setup.bash && source ~/ros1_ws/devel/setup.bash && rosbag record -a -O ./bags/{file_name}.bag"
        ],shell=True, executable="/bin/bash")
    else:
        ROSBAG_RECORD = subprocess.Popen([f"source /opt/ros/noetic/setup.bash && source ~/ros1_ws/devel/setup.bash && rosbag record -a -O ./bags/{file_name}.bag"],shell=True, executable="/bin/bash")
    return JSONResponse(content={'message': 'Starting RosBag Record'}, status_code=200)

@app.get("/stop_rosbag_record")
async def stop_rosbag_record():
    global ROSBAG_RECORD
    if ROSBAG_RECORD is not None:
        kill(ROSBAG_RECORD.pid)
        ROSBAG_RECORD = None
    else:
        if ROSBAG_RECORD == None:   
            return JSONResponse(content={'message': 'Stopped RosBag Record'}, status_code=200)
        kill(ROSBAG_RECORD.pid)
    return JSONResponse(content={'message': 'Stopped RosBag Record'}, status_code=200)

@app.get("/rosbag_list")
async def rosbag_list():
    directory = "bags"
    if not os.path.exists(directory):
        return JSONResponse(json.dumps({"state": "absent-dir"}), status_code = 200)
    files = os.listdir(directory)
    if not files:
        return JSONResponse(content=json.dumps(json.dumps({"state": "empty"}), status_code = 200))
    
    # Directory has files
    files_list = {i+1: file for i, file in enumerate(files)}
    return JSONResponse(content=json.dumps({"state": "present", "files": files_list}, status_code = 200)
#    return JSONResponse(content={'message': 'Starting RosBag Record'}, status_code=200)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
