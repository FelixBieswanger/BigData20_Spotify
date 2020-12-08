# Big Data Projekt - Spotify

## Sommersemester 2020

In diesem Projekt wurde eine Realtime Spotify Recommendation Engine implementiert. Die Neuheit dabei ist, dass der Nutzer die Recomendation beeinflussen kann. Dafür kann der Nutzer im Dashboard Parameter wie Loudness oder Daniceness anpassen. Anschließend wird basierend auf derzeit spielenden Song sowie der eingestellten Parameter berechnet.

# Architekturbild:
![alt text](https://github.com/FelixBieswanger/BigData20_Spotify/blob/master/architekture.png?raw=true)


Ordnerstruktur:
- k8 : beinhaltet alle Files zum deployment auf Kubernetes mit Hilfe der Azure Cloud. Dabei liegen die Docker Images auf unserer Azure Container Registery oder in Dockerhub.
- mvp: beinhaltet alle Code Files (Python) sowie die entsprechenden Dockerfiles der Applikationslogik
