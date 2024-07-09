## Setup Instructions obv

1. **Clone the repo** 
   ```bash
   git clone https://github.com/lordofwizard/ros_webserver
    ```

2. **Install required dependencies** (make sure you have pip installed)
```bash
python3 -m pip install fastapi uvicorn[standard]
```

Now you can work on your FastAPI project within the isolated virtual environment. To run your FastAPI application, use:

```bash
cd ros_webserver
pyenv activate fastapi-env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
