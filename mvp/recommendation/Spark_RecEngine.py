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
# from neo4j.graph import *
from pyspark.sql.functions import from_json,to_json,struct,col, mean as _mean, lit, first

import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.5 pyspark-shell'



# SPARK SUBMIT
# org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,
# org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.5 

# WURSTMEISTER KAFKA
# kafka:2.11-2.0.0

# REUIREMENTS TXT
# pyspark==2.4.5,

# DOKU:        
# packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0


# =>
#                         kafka:      pyspark
# Spark Submit             
# Streaming kafka         0-8_2.11    :2.4.5
# SQL kafka               0-10_2.11   :2.4.5

# Wurstmeister Kafka
# kafka                   2.11-       2.0.0

# Requirements txt
#                                     :2.4.5
  
                            
# ---------------------------------------------  
    
# SOLL / Doku:
# SQL Kafka               0-10_2.12   :3.0.0
#                         0.11.0.0 or up

# ---------------------------------------------         
        
# Lokal:
# same
# same
# kafka                  1.4.7 
# pyspark                             2.4.5


# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Input: Initiales Laden der Tracks und zugehörigen Features aus Neo4J
''' 

#uri = "bolt://40.80.208.184:7687"
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

data_df.sample(10)

            

        
# --------------------------------------------------------------------------- #


#Get distances for all pairs of songs
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


#distances= [[list[0]['id'], list[-1]['id'], len(list)] for list in distance_list]
distances= [[graphpath.start_node.get('id'), graphpath.end_node.get('id'), len(graphpath)] for graphpath in distance_list]
distances= pd.DataFrame.from_dict(distances)


print("------")
distances.sample(10)




# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #



'''
Anlegen des Spark Projektes
''' 

sc = SparkContext("local[2]", "EuclideanDistanceOnSteroids") #1.Spark, Mesos, YARN URL or local, 2. appName-Parametr
ssc = StreamingContext(sc, 10) #Spark-Context-Object, Interval 10 seconds
spark= SparkSession(sc) \
    .builder.appName("EuclideanDistanceOnSteroids")\
    .master("local[4]")\
    .getOrCreate()
    
#sc.setLogLevel("DEBUG")
    
    
    

'''
Input: Current Song & current Parameters from Frontend
''' 

#Topic Current Song
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

#Topic Current Parameters
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
Transformation & Output: Standardisieren und Enrichment mit EuclideanDistance ausgehend von current Song
'''

#Initialer erster Song?

#MAKE SURE, THAT CURRENT SONG IS IN NEO4J
# => vllt Anweisung in Songs.py, dass der immer abgespielt

current_Song= '7GJClzimvMSghjcrKxuf1M'

def foreach_batch_distance(current_Song_ID, epoch_id):  
    global current_Song
    
    try:
        current_Song= current_Song_ID \
                .collect()[0]
                #Verified: Always takes last
                
        current_Song= current_Song[0]
        
    except:
        print("Except in Current Song")
        pass

stream_song = data_current_song.writeStream \
        .foreachBatch(foreach_batch_distance) \
        .start()
   

# --------------------------------------------------------------------------- #

def foreach_batch_distance(current_Parameters, epoch_id):    
    # print("-----------------")
    # print("-----------------")
    # print("-----------------")
    print("hi")
    # print("-----------------")
    # print("-----------------")
    
    # print(current_Parameters)
    
    # try:           
    #Get global variables
    global data_df
    global distances
    global current_Song
    global data
    
    
    a_list= current_Parameters.select("alpha").collect()
    a_list= [row[0] for row in a_list]
    
    w_list= current_Parameters.select("weight").collect()
    w_list= [row[0] for row in w_list]
    
    
    if len(a_list) is not 4 or len(w_list) is not 4:
        #nur einmalig ausgeführt
        #hier also stattdessen liste anders befüllen
        
        a_list= [1, 1, -1, 1]
        w_list= [1, 1, 1, 1]
        

        # raise ValueError('Alpha & Weight still empty')
        
    
    #Merge new distances
    distances_left= distances.loc[distances.iloc[:,0]==current_Song]
    distances_left= distances_left.iloc[:,[1, 2]]
    distances_left= distances_left.rename(columns={1: "id", 2: "neo_distance"})
    
    # raise ValueError('1')


    distances_right= distances.loc[distances.iloc[:,1]==current_Song]
    distances_right= distances_right.iloc[:,[0, 2]]
    distances_right= distances_right.rename(columns={0: "id", 2: "neo_distance"})

    
    distances_merge= distances_left.append(distances_right)
    distances_merge= distances_merge.drop_duplicates()
    
    # raise ValueError('3')
    
    
    data= data_df.copy()
    #raise ValueError("---" + data.to_string())
    
    data= data.merge(distances_merge, on='id', how='left')
    data['neo_distance']= data.neo_distance.fillna(100)  
    
    sqlCtx = SQLContext(sc)
    data = sqlCtx.createDataFrame(data)
    
    if data.count() == 0:
        raise ValueError('Stage 1')
    
    #data.show()
    
    # raise ValueError('2')
    
    #Parameter Subset
    data = data.select(["id", \
                        "name", \
                        "danceability", \
                        "loudness", \
                        "tempo", \
                        "neo_distance"])
        
    if data.count() == 0:
        raise ValueError('Stage 2')
        
    # raise ValueError('4')
        
 
    #Enables Parallel Processing on Different Nodes
    #data = sc.parallelize(data)
        
        
    # --------------------------------------------------------------------------- #
    #PREPROCESSING
    # --------------------------------------------------------------------------- #        
    
    
    # Transform and write batchDF 
    from pyspark.ml.feature import VectorAssembler
    assembler = VectorAssembler() \
                        .setInputCols(["danceability", "loudness", "tempo", "neo_distance"]) \
                        .setOutputCol('features')
                        
    data = assembler.transform(data)
    
    if data.count() == 0:
        raise ValueError('Stage 3')

    # raise ValueError('5')     

    #Normalization
    from pyspark.ml.feature import MinMaxScaler
    scaler = MinMaxScaler(inputCol="features", 
                          outputCol="scaledFeatures")
    
    scalerModel = scaler.fit(data)
    
    if data.count() == 0:
        raise ValueError('Stage 4')
    
    data = scalerModel.transform(data)
    
    data = data.select(["id", \
                        "name", \
                        "scaledFeatures"])   
        

        
    if data.count() == 0:
        raise ValueError('Stage 5')
        
    # raise ValueError('6') 
    
    #raise ValueError('Rows' + str(data.collect()))
        
        
    # --------------------------------------------------------------------------- #
    #ENRICH WITH EUCLIDEAN DISTANCE ON STEROIDS
    # --------------------------------------------------------------------------- #        

    current_song_feature_vector= data \
                            .select("scaledFeatures") \
                            .filter("id = '" + current_Song + "'") \
                            .collect()[0]
                            
    #raise ValueError('Rows' + str(current_song_feature_vector))
                            
    #raise ValueError('Value Error' + ''.join(current_song_feature_vector)) 
                                         
    p_list= list(current_song_feature_vector[0])    

    #raise ValueError('p' + str(p_list) + 'a' + str(a_list) + 'w' +  str(w_list)) 

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
            .orderBy('distances', ascending= True) \
            .head(10) \
                
            #.collect()[0]
            #TODO: FILTER CURRENT SONG
            #.filter("id not '" + current_Song + "'") \     
            
                
                
    # data = data.select(to_json(struct([col(c).alias(c) for c in data.columns])).alias("value"))
    # data = data.withColumn("key",lit("null"))
    
    # data = data.selectExpr("CAST(key as String)","CAST(value as String)")
    
    # avg_stream = data.writeStream\
    #     .format("kafka")\
    #     .option("kafka.bootstrap.servers", "kafka:9092")\
    #     .option("topic", "graphdata")\
    #     .option("startingOffsets", "latest")\
    #     .option("checkpointLocation","./checkpoints")\
    #     .outputMode("complete")\
    #     .start()
        
    # avg_stream.awaitTermination()


    '''       
    recommendations= [id[0] for id in data]
    json_recommendations= {"songs": recommendations}
    message = json.dumps(coords).encode("ascii")
    '''


    # raise ValueError('6')                           
            
    # # --------------------------------------------------------------------------- #
    # #OUTPUT AN FRONTEND MIT KAFKA
    # # --------------------------------------------------------------------------- #  

    #raise ValueError('Wir haben es eigentlich geschafft')
    
    #raise ValueError('Rowslalall' + str(data.collect()))
        
    
    '''
    HOPEFULLY TODO: ALS JSON PARSEN
    '''

    data.selectExpr("id as value") \
        .selectExpr("CAST(value AS STRING)") \
        .write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("topic", "recommendations") \
        .save()
    

    # except Exception as e: 
    #     print("----")
    #     print(e)
    #     print("Except in Current Parameters")
    
    # raise ValueError('7') 
    
    pass
        


      

    
        
stream_param = data_current_parameter.writeStream \
        .foreachBatch(foreach_batch_distance) \
        .start()
        
        
        
def process_row(df, epoch_id):
    print("we lit")
    pass

stream_param2 = data_current_parameter.writeStream.foreachBatch(process_row).start()
        
        
            
consoleOutput = data_current_parameter.writeStream \
      .outputMode("append") \
      .format("console") \
      .start()
      
############   
   

userSchema_out = StructType().add("value", "string", True) \
    
out_test = spark.read \
            .format("kafka")\
            .option("kafka.bootstrap.servers", "kafka:9092")\
            .option("subscribe", "recommendations")\
            .load()       

out_test= out_test.selectExpr("CAST(value AS STRING)")                     
         
'''
Oder hier nicht als json converten
'''
# out_test = out_test.selectExpr("CAST(value AS STRING)")

# out_test = out_test \
#             .withColumn("value", from_json("value", userSchema_out)) \
#             .select(col('value.*')) \

      
out_test = out_test.writeStream \
      .outputMode("append") \
      .format("console") \
      .start()
      
############   
   
      
      
      
        


consoleOutput.awaitTermination()
  
stream_song.awaitTermination()
       
stream_param.awaitTermination()

stream_param2.awaitTermination()
            
out_test.awaitTermination()


