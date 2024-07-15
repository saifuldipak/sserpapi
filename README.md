# sserpapi
A small and simple ERP backend with REST API for Internet Service Providers
Tested on Ubuntu 22.04 with Python 3.10.12. See the api documentation for details of API resources.
Access API documentation using url http:://x.x.x.x:xxxx/docs. IP address and port number will depend 
on your configuration, please check details below


## Installation
There are two ways this application can be installed, one is stable release using binary wheel file  
another development version cloning source tree from Github(recommended for developers).If you use development source from Github,   
you can pull lattest commits from github to check new features.  

### Install using stable release wheel file
1. login to your linux machine and copy the installer into you home directory  
    `cp sserpapi-x.x.x-py3-none-any.whl /home/user_name/`  
2. create a virtual environment and activate  
    `cd /home/user_name`  
    `python3 -m venv .venv --prompt=sserpapi`    
    `source .venv/bin/activate`  
3. install   
    `pip install sserpapi-x.x.x-py3-none-any.whl`
4. create symlink  
    `ln -s .venv/lib/python3.10/site-packages/sserpapi sserpapi`

### Install using development version cloning source from Github  
1. clone the source tree  
`git clone https://github.com/saifuldipak/sserpapi.git`  

2. install in editable mode  
`cd sserpapi`  
`pip install -e .`

## Configuration and test run
1. edit .env file  
    `cd sserpapi`  
    `nano .env`  

    set FASTAPI_PATH to appropriate value  
    `FASTAPI_PATH=/home/user_name/sserpapi`
2. test run.
    `uvicorn sserpapi.main:app --host x.x.x.x:xxxx`

    x.x.x.x is the ip address of your server, if it has multiple ip addresses and you
    want to run on all interfaces it will be 0.0.0.0.
    xxxx is the port number, please make sure the port number is not used by any other application.
    for example-
    `uvicorn sserpai.main.app --host 192.168.1.20 --port 8001`
                        or
    `uvicorn sserpai.main.app --host 0.0.0.0 --port 8001`

    it should output like this, process id will be different  
    `INFO:     Started server process [244524]`  
    `INFO:     Waiting for application startup.`  
    `INFO:     Application startup complete.`  
    `INFO:     Uvicorn running on http://192.168.1.20:8001 (Press CTRL+C to quit)`  

    press CTRL+C to quit
3. API documentation  
    `http:://192.168.1.20:8001/docs`

## Create database and role/user in postgres
1. Login to your linux which is running postgresql server and then run following commands. replace 'postgres' with any other  
    super user account you have in your postgresl server.  
    `psql -U postgres`  
    `CREATE ROLE sserpapi LOGIN PASSWORD 'some_strong_password';`  
    `CREATE DATABASE sserp OWNER sserpapi;`  

## Create/update .env file
If sserpapi is installed from python wheel, '.env' file is present in the 'sserpapi' directory.Update sserpapi path, postgresql user and password in the file.

If not present, create the file with the following content, change the values as required- 

#Fastapi parameters  
FASTAPI_PATH='/home/user_name/sserpapi/sserpapi  

#Postgresql parameters  
POSTGRES_USER=sserpapi  
POSTGRES_PASSWORD=sserpapi009  
POSTGRES_HOST=127.0.0.1  
POSTGRES_PORT=5432  
POSTGRES_DB=sserp


## Deployement
You can deploy this app in many ways. here we have shown using 'systemd' and 'docker'  

### 1. configure and run this application using systemd   
    
`mkdir -p /home/user_name/.config/systemd/user`  
`cp sserpapi/scripts/sserpapi.service /home/user_name/.config/systemd/user`  
`systemctl --user enable --now sserpapi.service`  
`systemctl status sserpapi.service`  


## Create first admin user
`cd /home/user_name/sserpapi/sserpapi/scripts`

edit the username and password as per your need
`python3 reset_db.py`