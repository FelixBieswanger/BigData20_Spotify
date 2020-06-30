#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 14:51:50 2020

@author: davidrundel
"""


'''
Import verwendeter Bibliotheken
''' 

import pandas as pd
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from pyspark.sql.functions import lit
from pyspark.ml.linalg import VectorUDT, DenseVector
import pyspark.sql
from pyspark.sql import SQLContext
import math
import pyspark.mllib.linalg    
from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType
import pyspark.sql.functions as F
from scipy.spatial import distance
from neo4j import GraphDatabase



'''
Anlegen des Spark Projektes
''' 

sc = SparkContext("local[2]", "EuclideanDistanceOnSteroids") #1.Spark, Mesos, YARN URL or local, 2. appName-Parametr
ssc = StreamingContext(sc, 10) #Spark-Context-Object, Interval 10 seconds
spark= SparkSession(sc)





# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Input: Initiales Laden der Tracks und zugehörigen Features aus Neo4J
''' 

uri = "bolt://40.119.32.25:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "streams"))

Track_Feature_Query= "MATCH (n:Track) RETURN n"

with driver.session() as session:
    nodes = session.run(Track_Feature_Query)
    
    track_list= [] 
    
    for node in nodes:
        track_list.append(node.data())
        
track_list= [list(track.values())[0] for track in track_list]

data= pd.DataFrame.from_dict(track_list)

sqlCtx = SQLContext(sc)
data = sqlCtx.createDataFrame(data)
            

        
# --------------------------------------------------------------------------- #


#Get distances for all pairs of songs
Distance_Query="""MATCH (n:Track) WITH collect(n) as nodes UNWIND nodes as n 
UNWIND nodes as m WITH * WHERE id(n) < id(m) 
MATCH path = allShortestPaths( (n)-[*..]-(m) ) RETURN path"""

driver = GraphDatabase.driver(uri, auth=("neo4j", "streams"))

with driver.session() as session:
    nodes = session.run(Distance_Query)
    
    distance_list= [] 
    
    for node in nodes:
        distance_list.append(node.data())
        
driver.close()
  
distance_list= [list(distance.values())[0] for distance in distance_list]

distances= [[list[0]['id'], list[-1]['id'], len(list)] for list in distance_list]
distances= pd.DataFrame.from_dict(distances)





# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Input: Current Song & current Parameters from Frontend
''' 

#Topic Current Song
userSchema_Song = StructType().add("current_song", "string") \
    
data_current_song = spark.readStream \
            .format("kafka")\
            .option("kafka.bootstrap.servers", "kafka:{port1}")\
            .option("subscribe", "current_Song")\
            .load()
            # .option("sep", ",") \
            # .option("header", "true") \
            # .schema(userSchema_features) \
                
data_current_song = data_current_song.selectExpr("CAST(value AS STRING)")

data_current_song = data_current_song
            .withColumn("value", from_json("value", userSchema_Song)) \
            .select(col('value.*'))
            

        
# --------------------------------------------------------------------------- #

#Topic Current Parameters
userSchema_Parameters = StructType().add("parameter", "string") \
                        .add("alpha", "int") \
                        .add("weight", "int")
                        
data_parameters = spark.readStream \
            .format("kafka")\
            .option("kafka.bootstrap.servers", "kafka:{port1}")\
            .option("subscribe", "current_Parameters")\
            .load()
            # .option("sep", ",") \
            # .option("header", "true") \
            # .schema(userSchema_features) \
                
data_current_parameter = data_current_parameter.selectExpr("CAST(value AS STRING)")

data_current_parameter = data_current_parameter
            .withColumn("value", from_json("value", userSchema_Parameters)) \
            .select(col('value.*'))
    
    

    
    
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Transformation & Output: Standardisieren und Enrichment mit EuclideanDistance ausgehend von current Song
'''

#Initialer erster Song?
current_Song= '04DwTuZ2VBdJCCC5TROn7L'

stream = data_current_song.writeStream \
        .foreachBatch(foreach_batch_distance) \
        .start()
        
def foreach_batch_distance(current_Song_ID, epoch_id):  
    global current_Song
    
    current_Song= current_Song_ID
   
stream.awaitTermination()



# --------------------------------------------------------------------------- #


stream = data_current_parameter.writeStream \
        .foreachBatch(foreach_batch_distance) \
        .start()
        
    '''Stattdessen in ForEachBatch'''
    # .format("kafka")\
    # .option("kafka.bootstrap.servers", "kafka:9092")\
    # .option("topic", "graphdata")\
    # .option("startingOffsets", "latest")\
    # .option("checkpointLocation","./checkpoints")\
    # .outputMode("complete")\
    # .start()
        
def foreach_batch_distance(current_Parameters, epoch_id):  
    #Get global variables
    global data
    global distances
    global current_Song


    #Delete Previous Distances
    del data['neo_distance']

    
    #Merge new distances
    distances_left= distances.loc[distances.iloc[:,0]==current_Song]
    distances_left= distances_left.iloc[:,[1, 2]]
    distances_left= distances_left.rename(columns={1: "id", 2: "neo_distance"})
    
    distances_right= distances.loc[distances.iloc[:,1]==current_Song]
    distances_right= distances_right.iloc[:,[0, 2]]
    distances_right= distances_right.rename(columns={0: "id", 2: "neo_distance"})
    
    distances= distances_left.append(distances_right)
    distances= distances.drop_duplicates()
    
    data= data.merge(distances, on='id', how='left')
    data['neo_distance']= data.neo_distance.fillna(100)



    #Parameter Subset
    data = data.select(["id", \
                        "name", \
                        "danceability", \
                        "loudness", \
                        "tempo", \
                        "neo_distance"])
        
    #Enables Parallel Processing on Different Nodes
    data = sc.parallelize(data)
        
        
    # --------------------------------------------------------------------------- #
    #PREPROCESSING
    # --------------------------------------------------------------------------- #        
    
    
    # Transform and write batchDF 
    from pyspark.ml.feature import VectorAssembler
    assembler = VectorAssembler() \
                        .setInputCols(["danceability", "loudness", "tempo", "neo_distance"]) \
                        .setOutputCol('features')
                        
    data = assembler.transform(data)

      

    #Normalization
    from pyspark.ml.feature import MinMaxScaler
    scaler = MinMaxScaler(inputCol="features", 
                          outputCol="scaledFeatures")
    
    scalerModel = scaler.fit(data)
    
    data = scalerModel.transform(data)
    
    data = data.select(["id", \
                        "name", \
                        "scaledFeatures"])        
        
        
    # --------------------------------------------------------------------------- #
    #ENRICH WITH EUCLIDEAN DISTANCE ON STEROIDS
    # --------------------------------------------------------------------------- #        

    current_song_feature_vector= data \
                            .select(["scaledFeatures"]) \
                            .filter("id = '" + current_Song + "'") \
                            .collect()[0]
                                         
    p_list= list(current_song_feature_vector[0])                   
    a_list= current_Parameters.alpha        #z.B. [1, 1, 1, 1] 
    w_list= current_Parameters.weight       #z.B. [1, 1, 2, 1] 

    def euclDistance(q_list):
        try:
            distance= math.sqrt(sum( \
                                    [a * w * ((q - p) ** 2) + w * (1 if a==(-1) else 0) \
                                    for a, w, p, q  \
                                    in zip(a_list, w_list, p_list, q_list)]))
                
        except: 
            print("Except block!")
            distance= 0
            
        return distance

    euclDistanceUDF = F.udf(euclDistance, FloatType())      
    
    data = data.withColumn('distances', euclDistanceUDF('scaledFeatures'))
    
    data = data.select(['id', 'scaledFeatures', 'distances']) \
            .orderBy('distances', ascending= True) \
            .where('id not "' + current_song_ID + '"') \
            .take(5) \
            
                
            
    # --------------------------------------------------------------------------- #
    #OUTPUT AN FRONTEND MIT KAFKA
    # --------------------------------------------------------------------------- #      

    data.write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:{port1}") \
        .option("topic", "recommendations") \
        .save()
  
              
stream.awaitTermination()
            



