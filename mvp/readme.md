# Applikations Code

In diesem Ordner liegen alle Code Files. Dabei ist die Ordnerstuktur inhaltlich zu sehen. Jeder Ordner ist zuständig für eine Komponente des vorgeschlagenen Systems
und liegt mit eigenem Dockerfile "deploy-ready" bereit. Ausnahme hierbei sind die Komponenten Songs, Artists und Genres. Da innerhalb des Codes auf gemeinsame Ressourcen zurückgeriffen wird, liegen die entsprechenden Dockerfiles eine Stukuturebene über den anderen.

Nachfolgend eine kurze beschreibung der einzelen Komponten:
- api: Hilfskonstrukt, da der native Spotify Webplayer nur im Localhost funktioniert (oder mit SSL)
- artists: Hier werden Informationen der Artists gelesen und die entsprechende Nodes mit Realationship 1:n Songs in der Datenbank angelegt. Um die Anzahl der Anfragen an die API zu verringern wird der API-Endpunkt "get several artists" verwendet, bei dem man mit einer Anfrage Information über 50 verschiede Artists erhalten kann. Um die Beziehung zwischen Artist und Songs zu ermöglichen wird hierbei eine Mapping-Funktion implementiert.  
- songs: Hier werden Informationen zu den Songs gelesen und die entsprechende Nodes in der Datenbank angelegt. 
- neo4j: Normalerweise könnte man analog zu Kafka und Zookeeper das Images direkt von Dockerhub verwenden. Da wir jedoch das Streams-Plugin verwenden, dass die direkte Kommunikation zwischen Neo4j und Kafka ermöglich wird ein eigenständiges Dockerfile verwendet, dass das Streamsplugin in das Image kopiert.
- genre: Hier werden Informationen über die Genres der Artists gelesen und entsprechende Nodes mit Realationship zu 1:n Artists in der Datenbank angelegt.
- recommendation: Hier werden basierend auf den Parametern im Frontend Recomendations erzeugt und zurück an das Frontend geschickt.
- resources: Nach dem Prinzip der Objektorinentierung sind hier Klassen enthalten, die von in anderen Scripten häufig zur Verwendung kommen. Zum einen eine Kafka-Faktory die sich darum kümmert eine Verbindung zu dem Kafka-Broker zu erstellen. Dabei werden Prüfungen gemacht, ob der Kafka-Server schon bereit ist und vorallem auch, ob die Neo4J Datenbank auch schon bereit ist, da aus Kafka-Messages direkt Daten in der Datenbank angelegt werden. Zudem liegt hier die Spotify_Auth Klasse, die sich um die authentifizierten Kommunikation mit der Spotify-API kümmert.
- webplayer: Frontend der Applikation.  Wird mittels Flask umgesetzt, daher die Auteilung in "static" und "templates" Ordner. Die Logik ist im script.js file enthalten.
