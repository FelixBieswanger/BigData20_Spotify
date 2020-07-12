Big Data Projekt - Spotify

# Spark Recommendation Engine

Die Recommendation Engine wurde anhand eines Spark-Projektes realisiert. Um einer Vielzahl an Songs in der Neo4j und dem damit exponentiell skalierenden Rechenaufewandes gerecht zu werden (Tree Search Algorithmus), ermöglicht diese Komponente horizontal skalierende Pods.

Im ersten Schritt werden jegliche Songs aus der Neo4j-Datenbank in das Spark-Cluster geladen. Dies besetzt zwar einen großen Teil des Arbeitsspeichers, für die Berechnung neuer Recommendations werden jedoch jeweils alle Songs aus der Neo4j mit den zugehörigen Features benötigt. 

Weiterhin wird für alle Kombinationen aus 2 Songs eine Metrik berechnet (Neo4j-Distance). Diese wird initial für alle Kombinationen berechnet und erfordert eine aufwändige Query. Für eine Recommendation Engine mit wesentlich mehr Songs sollte diese Berechnung jeweils erst zur Anfragezeit einer neuen Recommendation und nicht intitial erfolgen. Bei diesem MVP wurde diese jedoch intitial implementiert, um die Zeit zwischen Anfrage und Antwort der Echtzeitapplikation zu reduzieren. 






reinladen songs- alle weil alle benötigt
reduktion um subset features

reinladen verbindungen - nur jeweilige weil sonst computational overhead



seperation of concerns
song kann sich ändern ohne dass parameter sich ändern und anders rum

current song
=>kein trigger
globale variable

current parameter

in dashboard jedes mal current song und danach current parameter

jedes mal wenn neue parameter, dann basierend auf current song n neue recommendations
diese laufen in dashboard reihe nach durch

in dashboard so dass mit jedem neuen song neu die parameter gesendet werden, sodass 1 recommendation ausreicht und für jeden song eine neue recommendation erzeugt wird






skalieren
wie dann anders
laufzeit

dijkstra übersteigt schnell rechenaufwand bei mehr tupeln



parallelisierbarkeit
standarddeviation
