# PUC-DevOps

PUC DevOps

Python

    To install packges
        pip install -r requirements.txt
    
    To Test Local
        fastapi dev <ARQUIVO>.py
    
    To change port on API
        fastapi dev <ARQUIVO>.py --port <PORTA>
        
    To Test API - Swagger
        https://<URL>/docs

NGINX

    Install
        sudo apt update && sudo apt install nginx -y
    Check Sintax
        sudo nginx -t
    Status
        sudo service nginx status
    Start
        sudo service nginx start
    Restart
        sudo service nginx restart

    Copy default.conf to NGINX Conf
        sudo cp default.conf /etc/nginx/conf.d/

    Find and kill port in execution
        sudo netstat -atunp | grep 8000
        sudo kill <PID>

Tests

    To test the application
        pytest tests/
    
    To see coverage
        pytest --cov

    To generate HTML report
        pytest --cov --cov-report=html

Verify

    Code quality
        pylint <ARQUIVO>.py

    Code analiser
        bandit <ARQUIVO>.py

Docker

    Build Image
        docker build -t <aplicacao>:<versão> <diretório>
            Ex.: docker build -t tarefas:1.0 .
    
    Run Image
        docker run -it -p <port1>:<port2> <aplicacao>:<versão>
            Ex.: docker run -it -p 8001:8000 tarefas:1.0

MySQL DB

    Run mysql DB
        docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql
    
    See Container status
        docker ps
            See Conteiner ID ( Ex.: fa3753fc54d4 )
        
    Exec MySQL
        docker exec -it <CONTAINR_ID> mysql -uroot -p
            create database <DATABASE_NAME>;
            exit;
