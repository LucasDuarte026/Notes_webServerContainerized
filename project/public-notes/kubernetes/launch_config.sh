# Ensure you are in your project root
# cd ~/Documents/cloud_computing_2025/project/public-notes


echo "Bringing the environment variables"
eval $(minikube -p minikube docker-env)

echo "Building the images to kubernetes:"
docker build -t pn-db:1.0 ./db
docker build -t pn-web:1.0 ./web
docker build -t pn-haproxy:1.0 ./loadbalancer

echo "Applying Kubernetes manifests..."

# --- 1. Database (db) ---
echo "Applying DB PVC and Secret..."
kubectl apply -f kubernetes/db/db-pvc.yaml
kubectl apply -f kubernetes/db/db-secret.yaml

echo "Applying DB Deployment and Service..."
kubectl apply -f kubernetes/db/db-deployment.yaml
kubectl apply -f kubernetes/db/db-service.yaml

# --- 2. Web Application (web) ---
echo "Applying Web Deployment and Service..."
kubectl apply -f kubernetes/web/web-deployment.yaml
kubectl apply -f kubernetes/web/web-service.yaml

# --- 3. HAProxy (loadbalancer) ---
echo "Applying HAProxy ConfigMap, Deployment, and Service..."
kubectl apply -f kubernetes/haproxy/haproxy-configmap.yaml
kubectl apply -f kubernetes/haproxy/haproxy-deployment.yaml
kubectl apply -f kubernetes/haproxy/haproxy-service.yaml

echo "All manifests applied. Waiting for resources to become ready..."
