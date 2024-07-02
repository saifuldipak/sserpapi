# sserpapi
A small and simple ERP backend with REST API for Internet Service Providers
Tested on Ubuntu 22.04 with Python 3.10.12. See the api documentation for details of API resources.
Access API documentation using url http:://x.x.x.x:xxxx/docs. IP address and port number will depend 
on your configuration, please check details below


## Installation
1. copy the installer into you prefered directory  
    `cp sserpapi-x.x.x-py3-none-any.whl /path/to/your/project`  
2. create a virtual environment in the /path/to/your/project directory and activate  
    `cd /path/to/your/project`  
    `python3 -m venv .venv`    
    `source .venv/bin/activate`  
3. install   
    `pip install sserpapi-x.x.x-py3-none-any.whl`
4. create symlink  
    `ln -s .venv/lib/python3.10/site-packages/sserpapi sserpapi`

## Configuration and test run
1. edit .env file  
    `cd sserpapi`  
    `nano .env`  

    set FASTAPI_PATH to appropriate value  
    `FASTAPI_PATH=/path/to/your/project/sserpapi`
2. test run  
    `uvicorn sserpapi.main:app`

    it should output like this, process id will be different  
    `INFO:     Started server process [244524]`  
    `INFO:     Waiting for application startup.`  
    `INFO:     Application startup complete.`  
    `INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)`  

    press CTRL+C to quit
3. API documentation  
    `http:://127.0.0.1:8000/docs`

## Deployement
1. configure and run this application using systemd
    `cp sserpapi/scripts/sserpapi.service /etc/systemd/system`
    `sudo systemctl enable --now sserpapi.service`
    `systemctl status sserpapi.service`


