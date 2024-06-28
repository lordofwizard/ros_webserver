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

def kill(pid):
    os.kill(pid, signal.SIGTERM)  # SIGKILL , SIGTERM

def start_proc(command: str, package_name: str, launch_file: str) -> subprocess.Popen:
    proc = subprocess.Popen([
        command,
        package_name,
        launch_file,
    ])
    return proc

@app.post("/save_rosbag")
async def save_rosbag(name: str = Form(...)):
    if not name:
        return JSONResponse(content={'error': 'Name is required'}, status_code=400)
    return JSONResponse(content={'message': f'Name received: {name}'}, status_code=200)

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

@app.get("/usb_cam")
async def usb_cam():
    global USBCAM
    if USBCAM is not None:
        kill(USBCAM.pid)
        USBCAM = start_proc("roslaunch", "usb_cam", "2_usb_cam.launch")
    else:
        USBCAM = start_proc("roslaunch", "usb_cam", "2_usb_cam.launch")
    return JSONResponse(content={'message': 'Starting USB Cam'}, status_code=200)

@app.get("/robot_bringup")
async def robot_bringup():
    global BRINGUP
    if BRINGUP is not None:
        kill(BRINGUP.pid)
        BRINGUP = start_proc("roslaunch", "tortoisebot_firmware", "bringup.launch")
    else:
        BRINGUP = start_proc("roslaunch", "tortoisebot_firmware", "bringup.launch")
    return JSONResponse(content={'message': 'Starting Robot Bringup'}, status_code=200)

@app.post("/start_rosbag_record")
async def start_rosbag_record(file_name: str = Form(...)):
    if not file_name:
        return JSONResponse(content={'error': 'Filename is required'}, status_code=400)
    return JSONResponse(content={'message': 'Starting RosBag Record'}, status_code=200)

@app.get("/rosbag_list")
async def rosbag_list():
    return JSONResponse(content={'message': 'Starting RosBag Record'}, status_code=200)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
