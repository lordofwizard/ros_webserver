from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from typing import Optional
import subprocess
import os
import signal
import uvicorn
import json 
import yaml
app = FastAPI()

# GLOBAL PROCESSES
BRINGUP = None
STARTTCP = None
USBCAM = None
ROSBAG = None
ROSBAG_RECORD = None

config_file_path = "config.yaml"
config = ""

with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)



def kill(pid):
    os.kill(pid, signal.SIGTERM)

def start_proc(command: str, package_name: str, launch_file: str) -> subprocess.Popen:
    command = f'source {config["ros"]["ros_setup"]} && source {config["ros"]["workspace_setup"]} && {command} {package_name} {launch_file}'
    proc = subprocess.Popen([
        command
    ],
    shell=True,
    executable="/bin/bash")
    return proc

def check_or_create_bags_directory():
    #directory = "bags"
    directory = config["rosbag"]["save_directory"]

    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory for Bags already '{directory}' created.")
    else:
        print(f"Directory for Bags already '{directory}' already exists.")

def kill_roslaunch_processes():
    try:
        ps_output = subprocess.check_output(['ps', 'aux'])
        ps_output = ps_output.decode('utf-8')
        processes = [line for line in ps_output.split('\n') if 'ros' in line]
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
async def rosbag_play(file_name: str = Form(...), speed: Optional[int] = Form(None)):
    global ROSBAG

    if not file_name:
        return JSONResponse(content={'error': 'Filename is required'}, status_code=400)
    if ROSBAG is not None:
        return JSONResponse(content={'error': 'already Rosbag Simulation Running'}, status_code=409)
    if os.path.exists("./bags/"+file_name+".bag") == False:
        return JSONResponse(content={'error': f'{file_name}.bag file not found'}, status_code=404)
    elif speed is not None:
        ROSBAG = subprocess.Popen([f'source {config["ros"]["ros_setup"]} && source {config["ros"]["workspace_setup"]} && rosbag play ./bags/{file_name}.bag -r {speed}'],shell=True, executable="/bin/bash")
        return JSONResponse(content={'message': f'rosbag play started with rate={speed}:'}, status_code=200)
    else:
        ROSBAG = subprocess.Popen([f'source {config["ros"]["ros_setup"]} && source {config["ros"]["workspace_setup"]} && rosbag play ./bags/{file_name}.bag'],shell=True, executable="/bin/bash")
        return JSONResponse(content={'message': 'rosbag play started'}, status_code=200)
    return JSONResponse(content={'message': 'Name received:'}, status_code=200)

@app.get("/stop_rosbag_play")
async def stop_rosbag_play():
    global ROSBAG
    if ROSBAG is not None:
        kill(ROSBAG.pid)
    else:
        return JSONResponse(content={'message': 'No rosbag simulation found'}, status_code=404)
    ROSBAG = None
    return JSONResponse(content={'message': 'Stopped rosbag simulation'}, status_code=200)

@app.get("/start_tcp")
async def start_tcp():
    global STARTTCP
    if STARTTCP is not None:
        return JSONResponse(content={'message': 'Already TCP End Point Running'}, status_code=409)
    else:
        STARTTCP = start_proc("roslaunch", config["start_tcp"]["package_name"], config["start_tcp"]["launch_file"])
    return JSONResponse(content={'message': 'Starting TCP'}, status_code=200)

@app.get("/stop_tcp")
async def stop_tcp():
    global STARTTCP
    if STARTTCP is not None:
        kill(STARTTCP.pid)
    else:
        return JSONResponse(content={'message': 'TCP End Point Not Found'}, status_code=404)
    STARTTCP = None
    return JSONResponse(content={'message': 'Killed TCP'}, status_code=200)


@app.get("/usb_cam")
async def usb_cam():
    global USBCAM
    if USBCAM is not None:
        return JSONResponse(content={'message':'USB Cam Process found, stop already running process'}, status_code=409)
    else:
        USBCAM = start_proc("roslaunch", config["usb_cam"]["package_name"], config["usb_cam"]["launch_file"])
        #return JSONResponse(content={'message':'No Camera Process found'}, status_code=404)
    return JSONResponse(content={'message': 'Starting USB Cam'}, status_code=200)


@app.get("/stop_usb_cam")
async def stop_usb_cam():
    global USBCAM
    if USBCAM is not None:
        kill(USBCAM.pid)
        USBCAM = None
    else:
        return JSONResponse(content={'message':'No Camera Process found'}, status_code=404)
    return JSONResponse(content={'message': 'Killing USB Cam'}, status_code=200)

@app.get("/robot_bringup")
async def robot_bringup():
    global BRINGUP
    if BRINGUP is not None:
        return JSONResponse(content={'message': 'Bringup already running'}, status_code=409)
    else:
        BRINGUP = start_proc("roslaunch", config["bringup"]["package_name"], config["bringup"]["launch_file"])
    return JSONResponse(content={'message': 'Starting Robot Bringup'}, status_code=200)

@app.get("/stop_bringup")
async def stop_bringup():
    global BRINGUP
    if BRINGUP is not None:
        #kill_roslaunch_processes()
        kill(BRINGUP.pid)
        BRINGUP = None
    else:
        return JSONResponse(content={'message': 'Bringup Process Not found'}, status_code=404)
    return JSONResponse(content={'message': 'Stopped Robot Bringup'}, status_code=200)

@app.post("/start_rosbag_record")
async def start_rosbag_record(file_name: str = Form(...), topics: str = Form(...), ):
    check_or_create_bags_directory()
    global ROSBAG_RECORD,BRINGUP
    if not file_name:
        return JSONResponse(content={'error': 'Filename is required'}, status_code=400)
    if os.path.exists("./bags/"+file_name+".bag"):
        return JSONResponse(content={'error': 'File already present'}, status_code=409)
    if ROSBAG_RECORD is not None:
        return JSONResponse(content={'error': 'Recording Already Running'}, status_code=409)
    else:
        if BRINGUP is not None:
            ROSBAG_RECORD = subprocess.Popen([f'source {config["ros"]["ros_setup"]} && source {config["ros"]["workspace_setup"]} && rosbag record -a -O ./bags/{file_name}.bag {topics}'],shell=True, executable="/bin/bash")
        else:
            return JSONResponse(content={'message': 'No Bringup Running found'}, status_code=404)
    return JSONResponse(content={'message': 'Starting RosBag Record'}, status_code=200)

@app.get("/stop_rosbag_record")
async def stop_rosbag_record():
    global ROSBAG_RECORD
    if ROSBAG_RECORD is not None:
        kill(ROSBAG_RECORD.pid)
        ROSBAG_RECORD = None
    else:
        return JSONResponse(content={'message': 'No Recording Currently Active'}, status_code=404)
    return JSONResponse(content={'message': 'Stopped RosBag Record'}, status_code=200)

@app.get("/rosbag_list")
async def rosbag_list():
    #directory = "bags"
    directory = config["rosbag"]["save_directory"]
    if not os.path.exists(directory):
        return JSONResponse(content=json.dumps({"state": "absent-dir"}), status_code = 404)
    files = os.listdir(directory)
    if not files:
        return JSONResponse(content=json.dumps({"state": "empty"}), status_code = 404)
    return JSONResponse(content={"state": "present", "files": files}, status_code = 200)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
