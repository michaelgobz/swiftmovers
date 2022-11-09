# Swift-movers-api

A swift-movers-api project is a portfolio project for the alx Holberton final project
It a proof of concept for logistics as a service system.
It uses a graphql server with python 3.11.0

## Installation and Usage
Clone the project.

Create a virtual environment:

```bash
python3.11.0 -m venv venv
source venv/bin/activate
cd venv/scripts/activate.bat for windows
```

Install everything needed:
```bash
pip install -r requirements.txt
```

Create the database and run the server:
```bash
python swiftmovers/manage.py migrate
python swiftmovers/manage.py runserver
```
Server runs at root
You should be able to access the server on [here](http://localhost:8000/). 

# Documentation
