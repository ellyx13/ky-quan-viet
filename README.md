# ky quan viet api

## Getting Started

### Prerequisites

- [Python](https://www.python.org/)
- [Pip](https://pip.pypa.io/en/stable/installation/)
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Cloning the Repository
First, clone the repository from GitLab and navigate into the project directory:
```bash
git clone https://github.com/ellyx13/ky-quan-viet-api.git
cd ky-quan-viet-api
```

### Setting Up the Environment
1. Create a folder named `.env`:
```bash
mkdir .env
```

2. Create a file named `dev.env` inside the `.env` folder and fill it with the following content. You can get the `SECRET_KEY` from [this link](https://8gwifi.org/jwsgen.jsp) by selecting `HS512` and clicking "Generate JWS Keys". Then, copy the `SharedSecret`:
```plaintext
environment=dev
app_database_name=app
database_url=mongodb://db?retryWrites=true

# Authentication 
SECRET_KEY={ENTER_YOUR_SECRET_KEY}
ALGORITHM="HS512"
DEFAULT_ADMIN_EMAIL={ENTER_YOUR_DEFAULT_EMAIL}
DEFAULT_ADMIN_PASSWORD={ENTER_YOUR_DEFAULT_PASSWORD}
```

3. Create a file named `test.env` inside the `.env` folder, and add the following content:
```plaintext
ENVIRONMENT=test
database_url=mongodb://db-test?retryWrites=true
```

### Install pre-commit
1. Download [pre-commit](https://pre-commit.com/):
```bash
pip install pre-commit
```
2. Install pre-commit
```
pre-commit install
```

### Running on Linux

To start the project on a Linux machine:

1. Open your terminal.
2. Navigate to the project directory.
3. Run the following command to make the script executable and start the Docker containers:
```bash
chmod +x bin/linux/start.sh
bin/linux/start.sh
```

### Running on Windows

To start the project on a Windows machine:

1. Open Command Prompt or PowerShell.
2. Navigate to the project directory.
3. Run the following command to start the Docker containers:
```cmd
bin\windows\start.bat
```

This script will build and start the Docker containers for the FastAPI application and MongoDB database.

### Accessing the API
Once the containers are up and running, you can access the FastAPI application by navigating to:

```
http://localhost:8005
```

You can explore the automatically generated API documentation at:

- Swagger UI: [http://localhost:8005/docs](http://localhost:8005/docs)
- ReDoc: [http://localhost:8005/redoc](http://localhost:8005/redoc)

### Stopping the Project

To stop the Docker containers, use the following commands based on your operating system:

#### Linux & Windows

Press `Ctrl + C`

This will stop and remove the containers, networks, and volumes created by Docker Compose.