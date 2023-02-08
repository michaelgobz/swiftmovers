# Swift Movers Api

A swift-movers-api project is a portfolio project for the alx Holberton final project 
It a proof of concept for logistics as a service system. This includes all the activites and works 
needed in the logistics industry. The api is fully rest in nature and is easy to run based both locally and deployment.

It uses a graphql server with python 3.11.0


## Installation and Usage
Clone the project.
```bash
git clone https://github.com/michaelgobz/swiftmovers.git
git checkout integration 
```
## Create a virtual environment:

```bash
cd swiftmovers
python3.11.0 -m virtualenv venv
source venv/bin/activate for unix and linux systems
cd venv/scripts/activate.bat for windows
```

## Install the necessary dependencies:
```bash
pip install -r requirements.txt
```

## Create the database and run the server:
- The api used the postgres database v15. to get started with more information is available [here](https://www.postgresql.org/docs/)
- Firstly, download the database server on machine [here](https://www.postgresql.org/download/) complete the installation process 
- Create a user/role with the credentials below

  ```bash
  username :swiftAdmin
  password :swiftAdmin
- ```
- Create database ```swift```  via the commandline or using pg4 admin the administrative interface for postgresql
- run the following commands in your terminal to get the server running

```bash
python swiftmovers/manage.py migrate
python swiftmovers/manage.py runserver
```
The server runs on port 8000 the django's default
![server splash screen]()
You should be able to access the API server on [here](http://localhost:8000/graphql/). 

# Documentation
