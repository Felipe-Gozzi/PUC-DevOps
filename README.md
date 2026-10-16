# PUC-DevOps

PUC DevOps

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
