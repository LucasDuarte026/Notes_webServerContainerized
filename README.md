# Cloud Computing 2025
-   Hochschule hof
## Student:
- 🇧🇷 Lucas Sales Duarte 



sistema operacional referencia
Ubuntu 20.04
    git clone https://github.com/LucasDuarte026/cloud_computing
    sudo apt update -y && sudo apt upgrade -y

    install docker and docker compose
    sudo apt install docker -y

    cd ./cloud_computing/project/public-notes


    the architecture chosen was usind a reverse proxy with haproxy to make public the port 80, and hide the inside containers
    there are 2 networks, one between the proxy and the web, and other from the web with database. this way is the best form 
    for the project, is used a non volatile database volume, that is always attached to a host storage to, even the containers be destroyed, the data never be lost

1º docker compose:
    to launch the docker infraestrucure with both haproxy, the web application and the database, build with docker compose and the launch them.
    


docker compose build
docker compose up

then it will be deployed in the port: localhost:80

2º Kubernetes

first install minikube and kubectl  

https://minikube.sigs.k8s.io/
https://kubernetes.io/
 
After it, launch the configuration file that already launches the minikube and config everything.

To launch the application, runs:
minikube service haproxy

