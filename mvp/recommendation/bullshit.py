#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 18:10:25 2020

@author: davidrundel
"""

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



'''
Anlegen des Spark Projektes
''' 

sc = SparkContext("local[2]", "EuclideanDistanceOnSteroids") #1.Spark, Mesos, YARN URL or local, 2. appName-Parametr
ssc = StreamingContext(sc, 10) #Spark-Context-Object, Interval 10 seconds
spark= SparkSession(sc) \
   .builder.appName("EuclideanDistanceOnSteroids")\
   .master("local[4]")\
   .getOrCreate()





# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

'''
Input: Initiales Laden der Tracks und zugehörigen Features aus Neo4J
''' 

uri = "bolt://40.124.88.102:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "streams"))

Track_Feature_Query= "MATCH (n:Track) RETURN n"

with driver.session() as session:
   nodes = session.run(Track_Feature_Query)

   track_list= [] 

   for node in nodes:
       track_list.append(node.data())

track_list= [list(track.values())[0] for track in track_list]

data_df= pd.DataFrame.from_dict(track_list)





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
userSchema_Song = StructType().add("current_song", "string", True) \

data_current_song = spark.readStream \
           .format("kafka")\
           .option("kafka.bootstrap.servers", "localhost:9092")\
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
           .option("kafka.bootstrap.servers", "localhost:9092")\
           .option("subscribe", "current_parameters")\
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
current_Song= '04DwTuZ2VBdJCCC5TROn7L'

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
   try:           
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
           print("Error")
           raise ValueError('Alpha & Weight still empty')


       #Merge new distances
       distances_left= distances.loc[distances.iloc[:,0]==current_Song]
       distances_left= distances_left.iloc[:,[1, 2]]
       distances_left= distances_left.rename(columns={1: "id", 2: "neo_distance"})


       distances_right= distances.loc[distances.iloc[:,1]==current_Song]
       distances_right= distances_right.iloc[:,[0, 2]]
       distances_right= distances_right.rename(columns={0: "id", 2: "neo_distance"})


       distances= distances_left.append(distances_right)
       distances= distances.drop_duplicates()


       data= data_df.copy()


       data= data.merge(distances, on='id', how='left')
       data['neo_distance']= data.neo_distance.fillna(100)  

       sqlCtx = SQLContext(sc)
       data = sqlCtx.createDataFrame(data)


       #Parameter Subset
       data = data.select(["id", \
                           "name", \
                           "danceability", \
                           "loudness", \
                           "tempo", \
                           "neo_distance"])


       '''
       TODO: PARALLELIZE
       '''
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

       data = data.select(['id']) \
               .orderBy('distances', ascending= True) \

               #.collect()

               #TODO: FILTER CURRENT SONG
               #.where('id not "' + current_Song + '"') \

       #recommendations= [id[0] for id in data]
       # json_recommendations= {"songs": recommendations}
       # message = json.dumps(coords).encode("ascii")


       data.show()                            

       # # --------------------------------------------------------------------------- #
       # #OUTPUT AN FRONTEND MIT KAFKA
       # # --------------------------------------------------------------------------- #      

       data.selectExpr("id as value") \
           .write \
           .format("kafka") \
           .option("kafka.bootstrap.servers", "localhost:9092") \
           .option("topic", "recommendations") \
           .save()

   except Exception as e: 
       print("----")
       print(e)
       print("Except in Current Parameters")  


stream_param = data_current_parameter.writeStream \
       .foreachBatch(foreach_batch_distance) \
       .start()


# --------------------------------------------------------------------------- #


stream_song.awaitTermination()

stream_param.awaitTermination()