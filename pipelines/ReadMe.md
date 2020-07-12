# Pipeline

Um dem CI/CD-Paradigma gerecht zu werden, wurde für die Spark-Komponente eine Pipeline mithilfe Azure DevOps implementiert. 
Diese erzeugt nach einem Commit in den Master-Branch ein Image und deployed dieses auf der Azure Container Registry. 
Weiterhin wird ein Rolling-Update des entsprechenden Pods in die Wege geleitet.

Leider konnte im Rahmen dieses Projektes aus Zeitgründen kein Test-Case geschrieben werden, welcher Qualitätschecks mit neu erzeugten Pods durchführt und 
abhängig von deren Erfolg das Deployment beeinflusst.
