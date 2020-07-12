Big Data Projekt - Spotify

# Spark Recommendation Engine

Die Recommendation Engine wurde anhand eines Spark-Projektes realisiert. Um einer Vielzahl an Songs in der Neo4j und dem damit exponentiell skalierenden Rechenaufewand gerecht zu werden (Tree Search Algorithmus), ermöglicht diese Komponente horizontal skalierende Pods.

Im ersten Schritt werden jegliche Songs aus der Neo4j-Datenbank in das Spark-Cluster geladen. Dies besetzt zwar einen großen Teil des Arbeitsspeichers, für die Berechnung neuer Recommendations werden jedoch jeweils alle Songs aus der Neo4j mit den zugehörigen Features benötigt. 

Weiterhin wird für alle Kombinationen aus 2 Songs eine Metrik berechnet (Neo4j-Distance). Diese wird initial für alle Kombinationen kalkuliert und erfordert eine aufwändige Query. Für eine Recommendation Engine mit wesentlich mehr Songs sollte diese Berechnung jeweils erst zur Anfragezeit einer neuen Recommendation für ebendiese und nicht intitial für alle erfolgen. Bei diesem MVP wurde diese jedoch intitial implementiert, um die Zeit zwischen Anfrage und Antwort der Echtzeitapplikation zu reduzieren. 

Der Streaming-Aspekt der Applikation wird anhand 2 verschiedener Kafka-Inputs realisiert. Die Spark Structured Streaming API verarbeitet dabei Echtzeit-Informationen aus dem Frontend. Genauer werden jeweils die zurzeit gespielten Songs und zurzeit ausgewählten Parameter übermittelt. Im Sinne der Seperation of Concerns bilden diese jeweils seperate Data-Streams ab. Diese Inputs werden getrennt voneinander beachtet, da ein Songwechsel im Frontend unabhängig von einer durch den Nutzer induzierten Parameteränderung stattfindet. Außerdem ermöglicht diese lose Kopplung eine verstärkte Flexibilität in Bezug auf Neuentwicklungen des Ablaufs.

Der Trigger für die Erzeugung von Recommendations ist die Änderung von Parametern. Dann werden die n (derzeit 1) passendsten Recommendations sortiert an das Frontend gesendet. Es wird sichergestellt, dass der aktuelle Song aus dem Frontend ebenso konsistent mit der Abbildung durch eine globale Variable im Spark-Projekt ist.

Um die Recommendations zu erzeugen wurde ein dedizierter Algorithmus entwickelt. Dieser stellt eine Weiterentwicklung der Euclidean-Distance-Function dar und nutzt die Informationen über Songs, welche die Spotify API liefert. Im Detail wird für einen aktuellen Song und über diverse Features hinweg (zB Danceability), der Abstand des jeweiligen Features zu allen anderen Songs berechnet. Der minimale Abstand stellt dabei den ähnlichsten Song dar. Je nach spezifizierter Parameter-Ausprägung im Dashboard werden die Features verschieden stark gewichtet. Nicht zuletzt kann durch eine negative Gewichtung festgelegt werden, dass der Abstand über ein Feature hinweg maximiert werden soll und es werden somit Songs präferiert, welche mit Blick auf dieses Feature anders sind.

Eines dieser Features stellt die Neo4j-Distance dar. Dabei wird für jede Songkombination berechnet, wie viel Nodes der kürzeste Weg zwischen diesen beinhaltet. Es stellt somit ein Maß für die Ähnlichkeit der Songs dar. Je kürzer die Distanz, desto ähnlicher. Da nicht zwischen allen Songs eine Verbindung besteht, wurde ein Default Value festgelegt.

Um die Parameter bei der Berechnung von Recommendations ähnlich stark ins Gewicht fallen zu lassen (außer vom User spezifiziert), wurden diese standardisiert. Diese Berechnung kann gemäß des Map-Reduce-Algorithmus auf mehreren Nodes parallel ausgeführt werden und die jeweiligen Ergebnisse aggregiert werden.
