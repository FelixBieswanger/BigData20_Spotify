# Deployment Files


Für jede Komponente des MVPs sind hier die jeweiligen Kubernetes YAML Files enhalten.
Wichtig hierbei ist anzumerken, dass Kafka und Zookeeper direkt als fertige Images von Dockerhub verwendet wird und so nicht mehr als Dockerfiles im MVP Ordner auftauchen.

Neben den gängien K8s Instanzen wie Deployments und Services werden hierbei auch Horizontal Pod Autoscaler verwendet. Diese gewähren die automatische Skalierbarkeit der jeweiligen Pods. Ferner werden hierbei, basierend auf der Auslastung der jeweiligen vCPU's, weitere Replicas erzeugt.
