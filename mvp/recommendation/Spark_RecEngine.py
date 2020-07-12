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
from pyspark.sql.functions import from_json,to_json,struct,col, mean as _mean, lit, first

import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.5 pyspark-shell'





# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Input: Initiales Laden der Tracks und zugehörigen Features aus Neo4J
''' 

uri = "bolt://neo4j:7687/db/data"
driver = GraphDatabase.driver(uri, auth=("neo4j", "streams"), encrypted=False)

Track_Feature_Query= "MATCH (n:Track) RETURN n"

with driver.session() as session:
    nodes = session.run(Track_Feature_Query)
    
    track_list= [] 
    
    for node in nodes:
        track_list.append(node.data())
        
track_list= [list(track.values())[0] for track in track_list]

data_df= pd.DataFrame.from_dict(track_list)


            

        
# --------------------------------------------------------------------------- #

'''
Input: Initiales Laden der kürzesten Distanz je Song-Kombination
''' 

Distance_Query="""MATCH (n:Track) WITH collect(n) as nodes UNWIND nodes as n 
UNWIND nodes as m WITH * WHERE id(n) < id(m) 
MATCH path = allShortestPaths( (n)-[*..]-(m) ) RETURN path"""

driver = GraphDatabase.driver(uri, auth=("neo4j", "streams"), encrypted=False)

with driver.session() as session:
    nodes = session.run(Distance_Query)
    
    distance_list= [] 
    
    for node in nodes:
        distance_list.append(node.data())
        
driver.close()
  
distance_list= [list(distance.values())[0] for distance in distance_list]

distances= [[graphpath.start_node.get('id'), graphpath.end_node.get('id'), \
             len(graphpath)] for graphpath in distance_list]
    
distances= pd.DataFrame.from_dict(distances)





# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Anlegen des Spark Projektes
''' 

sc = SparkContext("local[2]", "EuclideanDistanceOnSteroids") 

spark= SparkSession(sc) \
    .builder.appName("EuclideanDistanceOnSteroids")\
    .master("local[4]")\
    .getOrCreate()
    
#sc.setLogLevel("DEBUG")





# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Input: Spark Structured Streaming des jeweilig aktuellen Songs im Frontend
''' 

userSchema_Song = StructType().add("current_song", "string", True) \
    
data_current_song = spark.readStream \
            .format("kafka")\
            .option("kafka.bootstrap.servers", "kafka:9092")\
            .option("subscribe", "current_song")\
            .load()                            
                
data_current_song = data_current_song.selectExpr("CAST(value AS STRING)")

data_current_song = data_current_song \
            .withColumn("value", from_json("value", userSchema_Song)) \
            .select(col('value.*')) \
            

        


# --------------------------------------------------------------------------- #

'''
Input: Spark Structured Streaming der jeweilig ausgewählten Parameter im Frontend
''' 

userSchema_Parameters = StructType().add("parameter", "string") \
                        .add("alpha", "double") \
                        .add("weight", "double")
                        
data_current_parameter = spark.readStream \
            .format("kafka")\
            .option("kafka.bootstrap.servers", "kafka:9092")\
            .option("subscribe", "current_Parameters")\
            .load()
            
data_current_parameter = data_current_parameter.selectExpr("CAST(value AS STRING)")

data_current_parameter = data_current_parameter \
            .withColumn("value", from_json("value", userSchema_Parameters)) \
            .select(col('value.*'))
    

  
    
  
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Transformation & Output: Festlegen des jeweiligen Songs aus Dashboard als globale Variable
'''

#Initialer erster Song
current_Song= '11dFghVXANMlKmJXsNCbNl'

def foreach_batch_song(current_Song_ID, epoch_id):  
    global current_Song
    
    try:
        current_Song= current_Song_ID.select("current_song") \
                .collect()[0]                
                
        current_Song= current_Song[0]
        
    except:
        print("Except in Current Song")
        pass

stream_song = data_current_song.writeStream \
        .foreachBatch(foreach_batch_song) \
        .start()


        


# --------------------------------------------------------------------------- #

'''
Transformation & Output: Erzeugen von Recommendations, basierend auf jeweiligen 
aktuellen Parametern und dem zuletz festgelegten aktuellen Song
'''

def foreach_batch_distance(current_Parameters, epoch_id):    
    global data_df
    global distances
    global current_Song
    global data
    
    #Jeweilige Alpha Parameter
    a_list= current_Parameters.select("alpha").collect()
    a_list= [row[0] for row in a_list]

    #Jeweilige Weight Parameter    
    w_list= current_Parameters.select("weight").collect()
    w_list= [row[0] for row in w_list]
    
    #Initiales Befüllen der Listen, falls keine Lieferung aus Dashboard
    if len(a_list) is not 4 or len(w_list) is not 4:        
        a_list= [1, 1, 1, 1]
        w_list= [1, 1, 1, 1]
    
    #Basierend auf aktuellem Song festlegen der jeweiligen Distanzen aller anderen zu diesem
    distances_left= distances.loc[distances.iloc[:,0]==current_Song]
    distances_left= distances_left.iloc[:,[1, 2]]
    distances_left= distances_left.rename(columns={1: "id", 2: "neo_distance"})

    distances_right= distances.loc[distances.iloc[:,1]==current_Song]
    distances_right= distances_right.iloc[:,[0, 2]]
    distances_right= distances_right.rename(columns={0: "id", 2: "neo_distance"})
    
    distances_merge= distances_left.append(distances_right)
    distances_merge= distances_merge.drop_duplicates()    
    
    data= data_df.copy()
    
    data= data.merge(distances_merge, on='id', how='left')
    data['neo_distance']= data.neo_distance.fillna(100)  
    
    #Überführen in Spark SQL Dataframe
    sqlCtx = SQLContext(sc)
    data = sqlCtx.createDataFrame(data)   
    
    #Subset der relevanten Parameter
    data = data.select(["id", \
                        "name", \
                        "danceability", \
                        "loudness", \
                        "tempo", \
                        "neo_distance"])

    #Enables Parallel Processing on Different Nodes
    #data = sc.parallelize(data)




        
    # --------------------------------------------------------------------------- #
    #PREPROCESSING
    # --------------------------------------------------------------------------- #        
    
    #Überführen in eine spark-proprietäre Datenstruktur
    from pyspark.ml.feature import VectorAssembler
    assembler = VectorAssembler() \
                        .setInputCols(["danceability", "loudness", "tempo", "neo_distance"]) \
                        .setOutputCol('features')
                        
    data = assembler.transform(data)

    #Standardisieren der Verteilungen je Parameter
    from pyspark.ml.feature import MinMaxScaler
    scaler = MinMaxScaler(inputCol="features", 
                          outputCol="scaledFeatures")
    
    scalerModel = scaler.fit(data)
    
    data = scalerModel.transform(data)
    
    data = data.select(["id", \
                        "name", \
                        "scaledFeatures"])   

        


        
    # --------------------------------------------------------------------------- #
    #ANREICHERN MIT EUCLIDEAN DISTANCE
    # --------------------------------------------------------------------------- #        

    current_song_feature_vector= data \
                            .select("scaledFeatures") \
                            .filter("id = '" + current_Song + "'") \
                            .collect()[0]
    
                                         
    p_list= list(current_song_feature_vector[0])    

    def euclDistance(q_list):        
        try:
            distance= math.sqrt(sum( \
                                    [a * w * ((q - p) ** 2) + w * (1 if a==(-1) else 0) \
                                    for a, w, p, q  \
                                    in zip(a_list, w_list, p_list, q_list)]))
                
        except: 
            print("Except block!")
            
        finally:   
            return distance

    euclDistanceUDF = F.udf(euclDistance, FloatType())      
    
    data = data.withColumn('distances', euclDistanceUDF('scaledFeatures'))
    
    data = data.select('id') \
            .where("distances > 0") \
            .orderBy('distances', ascending= True) \
            .limit(1)                  
            
            
            
            
            
    # # --------------------------------------------------------------------------- #
    # OUTPUT AN FRONTEND MIT KAFKA
    # # --------------------------------------------------------------------------- #  
    
    data = data.select(to_json(struct([col(c).alias(c) for c in data.columns])).alias("value"))

    data.selectExpr("CAST(value AS STRING)") \
        .write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("topic", "recommendations") \
        .save()
    
    pass
         
        
stream_param = data_current_parameter.writeStream \
        .foreachBatch(foreach_batch_distance) \
        .start()      
  
        
  
        
    
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Testing & Logging: Console Output
'''
   

#Current Parameter         
consoleOutput = data_current_parameter.writeStream \
      .outputMode("append") \
      .format("console") \
      .start()
      
      
      
      
# --------------------------------------------------------------------------- #

#Current Recommendation
userSchema_out = StructType().add("value", "string", True) \
    
out_test = spark.readStream \
            .format("kafka")\
            .option("kafka.bootstrap.servers", "kafka:9092")\
            .option("subscribe", "recommendations")\
            .load()       

out_test= out_test.selectExpr("CAST(value AS STRING)")                     
               
out_test = out_test.writeStream \
      .outputMode("append") \
      .format("console") \
      .start()   





# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Await Termination Statements
'''         

consoleOutput.awaitTermination()
  
stream_song.awaitTermination()
       
stream_param.awaitTermination()
        
out_test.awaitTermination()