# CS490_project
CS490 Code ChatGPT Translator

### Project Overview

We are creating a code translation tool that will allow users to translate blocks of code from one language to another. The project uses the GPT API to perform the translation. Technologies involved include the following:

- Backend: Python with Flask
- Frontend: React
- Database: MySQL
- Hosting/Deployment: Azure
- Testing: Jest

Responsibilities are broken down as follows:

| Name | Role |
|------|------|
| Hamdi Korreshi | Project Manager and DevOps |
| Jason Cho | Flex, Backend |
| Dzejla Arapovic | Frontend, Database, Backend |
| Matthew DeFranceschi | Backend, Database |
| Naman Raval | Frontend, Backend |

### Repository Structure
```
root/
 - backend/
 - - functions/
 - - db/
 - - api/
 - web/
 - - landing page
 - - about
 - - translation page
 - - admin/
 - .git/
 - .env
 - .gitignore
 - README.md
```

## Serve the app
`cd frontend` <br>
`npm start` starts frontend <br>
For WSL, `start-wsl-backend` starts backend for WSL with python3,
For UNIX, `npm run start-backend` starts backend <br>
For Windows, `npm run run-backend` starts backend

## Run test suite
`cd frontend` <br>
`npm run test-backend`

## PROJECT SETUP:
Follow https://dev.to/nagatodev/how-to-connect-flask-to-reactjs-1k8i for more extensive details <br>

Navigate to frontend directory <br>
`cd frontend` <br>
run `npm start`<br>
This may require some debugging <br>

In a new terminal, navigate to backend
`cd backend`
Create a virtual environment
```
For mac/unix users: python3 -m venv env
For windows users: py -m venv env
```
Activate the virtual environment
```
For mac/unix users: source env/bin/activate
For windows users: .\env\Scripts\activate
```

Install flask 
Run
`pip install flask` and `pip install python-dotenv`

In backend directory, run
`flask run`
or, if that does not work, run
`python -m flask run`

You may need to run `npm install axios`, I'm not sure.

## DATABASE SETUP:
For more information consult https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/

### Install MySQL  
For UNIX users (Debian/Ubuntu-based):
```
sudo apt update
sudo apt install mysql-server
```
Start MySQL server
`sudo service mysql start`
You can check the status with
`sudo service mysql status`

For Windows users:  
Visit the following page  
`https://dev.mysql.com/downloads/installer/`  
Download the installer and go through the setup wizard with default settings  
Make sure to select full install  

### Set up the `.env` file  
Create a new file named `.env` in backend  
Add the following information  
Make sure to update the MYSQL_PASSWORD if you set one for root  
```
MYSQL_HOST='localhost'
MYSQL_USER='root'
MYSQL_DB='codecraft'
MYSQL_PASSWORD=''
```

### Install the python dependencies
```
pip install mysql-connector
pip install python-dotenv
```
Run the DB setup script
```
cd backend
python db_setup.py
```

### Make sure the server is running (debugging)  
For UNIX users:  
`sudo service mysql status`  
For Windows users:  
Try `Get-Service -Name 'mysql*'` in PowerShell (untested)

### Troubleshooting
If you are having issues on UNIX, run:
`sudo mysql`
Once in MySQL:
`ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';`
