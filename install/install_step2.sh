sudo apt install conntrack
sudo minikube start --driver=none
sudo -s
sudo apt-get update && sudo apt-get install -y apt-transport-https gnupg2
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
wget https://github.com/kubeflow/kfctl/releases/download/v1.0.2/kfctl_v1.0.2-0-ga476281_linux.tar.gz
tar -xvf kfctl_v1.0.2-0-ga476281_linux.tar.gz
sudo mv kfctl /usr/bin/
export KF_NAME=kf-test
export BASE_DIR=/home/ubuntu/
export KF_DIR=${BASE_DIR}/${KF_NAME}
export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_k8s_istio.v1.0.2.yaml"
mkdir -p ${KF_DIR}
cd ${KF_DIR}
sudo kfctl apply -V -f ${CONFIG_URI}
export NAME=$(sudo kubectl get pods -n istio-system --selector=app=istio-ingressgateway -o jsonpath='{.items[*].metadata.name}')
sudo apt-get update
sudo apt-get install socat
sudo kubectl port-forward --address 0.0.0.0 $NAME -n istio-system 8888:80 &
