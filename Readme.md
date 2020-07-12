# Big Data Projekt - Spotify

## Sommersemester 2020


Ordnerstruktur:
- k8 : beinhaltet alle Files zum deployment auf Kubernetes mit Hilfe der Azure Cloud. Dabei liegen die Docker Images auf unserer Azure Container Registery. Wichtig hierbei ist anzumerken, dass Kafka und Zookeeper direkt als fertigen Images von Dockerhub verwendet wird. Diese komponenten tauchen nicht in einene Code Files im MVP order auf, spielen jedoch für die Kommunikation der Komponenten eine relevante Rolle.
- mvp: beinhaltet alle Code Files (Python) sowie die entsprechenden Dockerfiles 
