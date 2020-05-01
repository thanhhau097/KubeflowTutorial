# being error

FROM ubuntu:18.04

RUN apt update

RUN apt install -y curl
RUN curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube
RUN mkdir -p /usr/local/bin/
RUN install minikube /usr/local/bin/

RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh

RUN apt install -y systemd
RUN systemctl restart docker

RUN apt install conntrack
RUN minikube start --driver=none

RUN apt-get update && sudo apt-get install -y apt-transport-https gnupg2
RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
RUN echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
RUN sudo apt update
RUN sudo apt install -y kubectl

RUN wget https://github.com/kubeflow/kfctl/releases/download/v1.0.2/kfctl_v1.0.2-0-ga476281_linux.tar.gz
RUN tar -xvf kfctl_v1.0.2-0-ga476281_linux.tar.gz
RUN mv kfctl /usr/bin/
RUN export KF_NAME=kf-test
RUN export BASE_DIR=./
RUN export KF_DIR=${BASE_DIR}/${KF_NAME}
RUN export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_k8s_istio.v1.0.2.yaml"

RUN mkdir -p ${KF_DIR}
RUN cd ${KF_DIR}
RUN kfctl apply -V -f ${CONFIG_URI}

#RUN kubectl get pods -n istio-system
RUN export NAME=$(kubectl get pods -n istio-system --selector=app=istio-ingressgateway -o jsonpath='{.items[*].metadata.name}')
RUN sudo apt-get update
RUN sudo apt-get install socat
EXPOSE 8888
CMD kubectl port-forward --address 0.0.0.0 $NAME -n istio-system 8888:80