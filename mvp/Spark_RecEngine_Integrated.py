#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 14:51:50 2020

@author: davidrundel
"""


from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
import pandas as pd
from pyspark.sql.functions import lit
from pyspark.ml.linalg import VectorUDT, DenseVector




sc = SparkContext("local[2]", "EuclideanDistanceOnSteroids") #1.Spark, Mesos, YARN URL or local, 2. appName-Parametr
ssc = StreamingContext(sc, 10) #Spark-Context-Object, Interval 10 seconds
spark= SparkSession(sc)




# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #




'''
Input: Neo4J Output as Structured Streaming
''' 
userSchema_features = StructType().add("loudness", "double") \
                        .add("liveness", "double") \
                        .add("tempo", "double") \
                        .add("valence", "double") \
                        .add("instrumentalness", "double") \
                        .add("danceability", "double") \
                        .add("speechiness", "double") \
                        .add("mode", "double") \
                        .add("duration_ms", "double") \
                        .add("explicit", "boolean") \
                        .add("artists", "string") \
                        .add("acousticness", "double") \
                        .add("name", "string") \
                        .add("id", "string") \
                        .add("key", "double") \
                        .add("time_signature", "double") \
                        .add("energy", "double") 
                        
data_features= spark \
        .readStream \
        .option("sep", ",") \
        .option("header", "true") \
        .schema(userSchema_features) \
        .csv("/Users/davidrundel/Desktop/HdM/BigData/RecommDraft/Stream_From_Neo4j_Features")
        
data_features = data_features.select(["id", "name", "danceability", "loudness", "tempo"])

data_features = data_features.selectExpr("id as id_features", \
                                         "name as name_features", \
                                        "danceability as danceability", \
                                        "loudness as loudness", \
                                         "tempo as tempo")
        
# --------------------------------------------------------------------------- #

userSchema_distance = StructType().add("loudness", "double") \
                        .add("liveness", "double") \
                        .add("tempo", "double") \
                        .add("valence", "double") \
                        .add("instrumentalness", "double") \
                        .add("danceability", "double") \
                        .add("speechiness", "double") \
                        .add("mode", "double") \
                        .add("duration_ms", "double") \
                        .add("explicit", "boolean") \
                        .add("artists", "string") \
                        .add("acousticness", "double") \
                        .add("name", "string") \
                        .add("id", "string") \
                        .add("key", "double") \
                        .add("time_signature", "double") \
                        .add("energy", "double") 
                        
data_distance= spark \
        .readStream \
        .option("sep", ",") \
        .option("header", "true") \
        .schema(userSchema_features) \
        .csv("/Users/davidrundel/Desktop/HdM/BigData/RecommDraft/Stream_From_Neo4j_Distance")

data_distance = data_distance.selectExpr("id as id_distance", \
                                         "name as name_distance", \
                                         "acousticness as acousticness")
        
#data_distance = data_distance.select(["id", "name", "acousticness"]) 




#data_distance.join(data_features, on="id", how="Inner")

from pyspark.sql.functions import expr

joined_data= data_distance.join(data_features,
                   expr("id_distance = id_features"))

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #




'''
Transformation: Standardisieren und Enrichment mit EuclideanDistance ausgehend von current Song
'''

#trackid usw mit persist
#abstände immer nur temporär

# def foreach_batch_features(data, epoch_id):
    
#     # Transform and write batchDF   
#     from pyspark.ml.feature import VectorAssembler
#     assembler = VectorAssembler() \
#                         .setInputCols(["danceability", "loudness", "tempo"]) \
#                         .setOutputCol('features')
                        
#     data_features = assembler.transform(data)
    
    
#     from pyspark.ml.feature import StandardScaler
#     scaler = StandardScaler(inputCol="features",
#                             outputCol="scaledFeatures",
#                             withStd=True, withMean=True)
    
#     # Compute summary statistics by fitting the StandardScaler
#     scalerModel = scaler.fit(data_features)
    
#     # Normalize each feature to have unit standard deviation and mean 0.
#     data_features = scalerModel.transform(data_features)
    
#     #from pyspark.ml import Pipeline
#     #pipeline= Pipeline().setStages([assembler, scaler])
    
#     data_features = data_features.select(["id_features", "name_features", "scaledFeatures"])
    
#     data_features.persist()

#     #Kafka Sink an Dashboard    
#     # data.persist()
#     # data.write.format(...).save(...) 
#     # data.unpersist()

# stream_features = data_features.writeStream \
#         .foreachBatch(foreach_batch_features) \
#         .start()
        
# --------------------------------------------------------------------------- #



def foreach_batch_distance(data, epoch_id):
    
    # Transform and write batchDF 
    from pyspark.ml.feature import VectorAssembler
    assembler = VectorAssembler() \
                        .setInputCols(["danceability", "loudness", "tempo", "acousticness"]) \
                        .setOutputCol('features')
                        
    data = assembler.transform(data)

      
    # from pyspark.ml.feature import StandardScaler
    # scaler = StandardScaler(inputCol="features",
    #                         outputCol="scaledFeatures",
    #                         withStd=True, withMean=True)
    
    from pyspark.ml.feature import MinMaxScaler
    scaler = MinMaxScaler(inputCol="features", 
                          outputCol="scaledFeatures")
    
    # Compute summary statistics by fitting the StandardScaler
    scalerModel = scaler.fit(data)
    
    # Normalize each feature to have unit standard deviation and mean 0.
    data = scalerModel.transform(data)
    
    # from pyspark.ml.feature import Normalizer
    # normalizer = Normalizer(inputCol="features",
    #                         outputCol="scaledFeatures")
    
    # data = normalizer.transform(data)
    
    
    
    data = data.select(["id_distance", \
                        "name_distance", \
                        "scaledFeatures"])

    
    
    
    
    
    # Current Song
    current_song_ID= '2glGP8kEfACgJdZ86kWxhN'

    current_song_feature_vector= data \
                            .select(["scaledFeatures"]) \
                            .filter("id_distance = '" + current_song_ID + "'") \
                            .collect()[0]
                                         
    p_list= list(current_song_feature_vector[0])                   

                            
                            
    # Current Weights

    # Calculate Euclidean Distance to other Songs
    import math
    import pyspark.mllib.linalg

    # val euclideanDistance = udf { (v1: Vector, v2: Vector) =>
    #         sqrt(Vectors.sqdist(v1, v2))
    # }
    
    from pyspark.sql.functions import udf
    from pyspark.sql.types import FloatType
    import pyspark.sql.functions as F
    from scipy.spatial import distance
    
    '''
    EUCLIDEAN DISTANCE ON STEROIDS
    '''

#   n = 0                       #Amount of parameteres
    a_list = [1, -1, 1, 1]      #Index if parameter i is same, wayne or contrary
    w_list = [1, 1, 2, 1]       #Weight of parameter i
#   p = []                      #Value of parameter i for current song
#   q = []                      #Value of parameter i for potential next song
#   b_list = [0, 1, 0, 0]       #Standard deviation for parameter i, gets added if contrary
    'how to generate this automatically? Function is 1 if a is -1'
    

    def euclDistance(q_list):
        try:
            distance= math.sqrt(sum( \
                                    [a * w * ((q - p) ** 2) + w * (1 if b==(-1) else 0) \
                                    for a, w, p, q, b  \
                                    in zip(a_list, w_list, p_list, q_list, b_list)]))
                
        except: 
            print("Except block!")
            distance= 0
            
        return distance


    euclDistanceUDF = F.udf(euclDistance, FloatType())      
    
    data = data.withColumn('distances', euclDistanceUDF('scaledFeatures'))
    
    
    
    
    
    #euclideanDistance = F.udf(lambda x: distance.euclidean(x, current_song_feature_vector), FloatType())
    # euclideanDistance = F.udf(lambda x: \
    #                           math.sqrt(sum([(v1_p - v2_p) ** 2 \
    #                                          for v1_p, v2_p \
    #                                          in zip(x, current_song_feature_vector)])), \
    #                           FloatType())
        
    # euclideanDistanceOnSteroidsUDF = F.udf(lambda q_list: \
    #                                         math.sqrt(sum( \
    #                                         [a * w * ((q - p) ** 2) + w * b \
    #                                         for a, w, p, q, b  \
    #                                         in zip(a_list, w_list, p_list, q_list, b_list)])), \
    #                                         FloatType())
  
    '''
    def euclideanDistanceOnSteroids(q_list):
        distance= math.sqrt(sum( \
                                [a * w * ((q - p) ** 2) + w * b \
                                for a, w, p, q, b  \
                                in zip(a_list, w_list, p_list, q_list, b_list)]))
            
        return distance


    euclideanDistanceOnSteroidsUDF = F.udf(lambda q_list: euclideanDistanceOnSteroids(q_list), FloatType())      
        
    # for row in data.select('scaledFeatures').collect():
    #     print("----------")
    #     print(row[0]) 
    #     print("----------")
    
    data = data.withColumn('distances', \
                           [euclideanDistanceOnSteroidsUDF(lit(row[0])) \
                            for row in data.select('scaledFeatures').collect()])
    '''
    
    

        
        
    
        
    # def euclideanDistanceOnSteroids(q_list):
        
    #     q_list['distance']= [euclideanDistanceOnSteroidsUDF(row) for row in q_list['scaledFeatures']]
    #     print(q_list['distance'])
        
    #     return q_list['distance']
        
        # q_list['distance']= euclideanDistanceOnSteroidsUDF(q_list['scaledFeatures'])
        # print(q_list)
        
        # return q_list['distance']
        
        # for row in q_list.scaledFeatures:
        
        # try:
        #     distance= euclideanDistanceOnSteroidsUDF(q_list)
            
        # except:
        #     distance= 0
            
        # return distance
        
    #data = data.withColumn('distances', euclideanDistanceOnSteroids(F.col('scaledFeatures')))
    #data = data.withColumn('distances', euclideanDistanceOnSteroidsUDF('scaledFeatures'))
    # print(data.select('scaledFeatures'))
    # print("----------")
    # print(data.select('scaledFeatures').collect())
    # print("----------")
    # print(data.select('scaledFeatures').collect()[0])
    # print("----------")
    # print("----------")
    

    
    
    # euclideanDistance = udf(lambda v1: \
    #                         math.sqrt(sum([(v1_p - v2_p) ** 2 \
    #                         for v1_p, v2_p \
    #                         in zip(v1, current_song_feature_vector)])), \
    #                         FloatType())

    
    # data = data.withColumn("distance", \
    #                        euclideanDistance('scaledFeatures'))
    

    #Filtern des jetzigen Songs (Distance = 0,0)
    
    data.show(truncate=False)
    
    
    data = data.select(['id_distance', 'scaledFeatures', 'distances']) \
            .orderBy('distances', ascending= True) \
            .where('distances > 0.0') \
            .take(3) \
            

    
    '''BERECHNEN & AN KAFKA'''
    
    #data.persist()

    #Kafka Sink an Dashboard    
    # data.persist()
    # data.write.format(...).save(...) 
    # data.unpersist()

stream = joined_data.writeStream \
        .foreachBatch(foreach_batch_distance) \
        .start()










# from pyspark.ml.feature import StringIndexer
# stringindexer = StringIndexer() \
#         .setInputCol("boxId") \
#         .setOutputCol("boxId_si")

# from pyspark.ml.feature import OneHotEncoder
# onehotencoder = OneHotEncoder() \
#         .setInputCol("boxId_si") \
#         .setOutputCol("ohe_features")


# from pyspark.ml.feature import VectorAssembler
# vectorAssembler = VectorAssembler() \
#       .setInputCols(["ohe_features", \
#                      "last_acceleration", \
#                      "last_currentSpeed", \
#                       "rolling_avg_consumption", \
#                       "rolling_std_consumption"]) \
#       .setOutputCol("features")
      
# from pyspark.ml.regression import LinearRegression
# lr = LinearRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8) \
#     .setFeaturesCol("features") \
#     .setLabelCol("label")
    
    
# from pyspark.ml.tuning import ParamGridBuilder    
# paramGrid = ParamGridBuilder() \
#     .addGrid(lr.regParam, [0.1, 0.3, 0.6]) \
#     .addGrid(lr.elasticNetParam, [0.1, 0.5, 0.8]) \
#     .build()
    
# from pyspark.ml import Pipeline
# pipeline= Pipeline().setStages([stringindexer, onehotencoder, vectorAssembler, lr])
    
# from pyspark.ml.tuning import CrossValidator   
# from pyspark.ml.evaluation import RegressionEvaluator   
# crossval = CrossValidator(estimator=pipeline,
#                           estimatorParamMaps=paramGrid,
#                           evaluator=RegressionEvaluator(metricName="rmse"),
#                           numFolds=5)

# crossval = crossval.fit(static_df)

# from pyspark.sql.functions import *

# wd_avg_consumption= csvDF \
#             .withWatermark("timeStamp", "60 seconds") \
#             .groupBy("boxId", window("timeStamp", "60 seconds", "15 seconds")) \
#             .agg(last("timeStamp").alias("last_timeStamp"), \
#                   last('acceleration').alias("last_acceleration"), \
#                 last('currentSpeed').alias("last_currentSpeed"), \
#                   count("consumption").alias("count_consumption"), \
#                   avg("consumption").alias("rolling_avg_consumption"), \
#                   stddev("consumption").alias("rolling_std_consumption"), \
#                   last("consumption").alias("label")) \
                
# predictions= model.transform(wd_avg_consumption)


  
# data = data.select(["id", "name", "danceability", "loudness", "tempo"])

# stream = data.writeStream \
#         .format("console") \
#         .start()

# --------------------------------------------------------------------------- #


# # Transform and write batchDF   
# from pyspark.ml.feature import VectorAssembler
# assembler = VectorAssembler() \
#                     .setInputCols(["danceability", "loudness", "tempo"]) \
#                     .setOutputCol('features')
                    
# data = assembler.transform(data)



# from pyspark.ml.feature import StandardScaler
# scaler = StandardScaler(inputCol="features",
#                         outputCol="scaledFeatures",
#                         withStd=True, withMean=True)

# # Compute summary statistics by fitting the StandardScaler
# scalerModel = scaler.fit(data)

# # Normalize each feature to have unit standard deviation and mean 0.
# data = scalerModel.transform(data)


# #from pyspark.ml import Pipeline

# #pipeline= Pipeline().setStages([assembler, scaler])
    
  
# stream = data.writeStream \
#         .format("console") \
#         .start()

# --------------------------------------------------------------------------- ## --------------------------------------------------------------------------- #



# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #




'''
Output: Distance pro Song als CSV in Frontend weitergeben
Alternativ: Top 5
'''

# stream= data
#     .writeStream \
#     .format("console") \
#     .start()
    
# # pred_stream_writejson= predictions \
# #     .writeStream \
# #     .format("json") \
# #     .option("checkpointLocation", \
# #             "/Users/davidrundel/Desktop/HdM/DataScience/Spark1Try/PredictionOutput/CheckpointLocation") \
# #     .option("path", \
# #             "/Users/davidrundel/Desktop/HdM/DataScience/Spark1Try/PredictionOutput/") \
# #     .start() \
# #     #.outputMode("complete") \
# #     #.outputMode("append") \
    
stream.awaitTermination()











# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #



























# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

def get_df():
    data= pd.read_csv("/Users/davidrundel/Desktop/HdM/BigData/RecommDraft/export-2.csv",sep=',')
    data= data['t']
    data= data.tolist()
    
    import re
    import ast
    
    def add_quotes_to_lists(match):
        return re.sub(r'([\s\[])([^\],]+)', r'\1"\2"', match.group(0))
    
    dict= []
    
    for s in data:
        #d = {i.split(': ')[0]: i.split(': ')[1] for i in s.split(',')}
        #print(d)
    
        s = re.sub(r':\s?(?![{\[\s])([^,}]+)', r': "\1"', s) #Add quotes to dict values
        s = re.sub(r'(\w+):', r'"\1":', s) #Add quotes to dict keys
    
        s = re.sub(r'\[[^\]]+', add_quotes_to_lists, s) #Add quotes to list items
    
        final = ast.literal_eval(s) #Evaluate the dictionary
        print(final)
        
        dict.append(final)
        
    data_expand= pd.DataFrame.from_dict(dict)
    data_expand.to_csv("/Users/davidrundel/Desktop/HdM/BigData/RecommDraft/TEMP_DB_QUERY.csv", index= False)


# import json
# d = json.loads(data)

# import hjson
# for line in data:
#     print(line)
#     #json_acceptable_string = line.replace("'", "\"")
#     #d = json.loads(json_acceptable_string)
#     hjson.loads(data)
    

# import ast
# for line in data:
#     print("hi")
#     curr_line=ast.literal_eval(line)
#     print(curr_line)
    



# data= [dict(line) for line in data]

# data = [dict(
#                item.replace("'", '').split(':')
#                for item in s[1:-1].split(', ')
#                )
#           for s in data]

# #first_row=(data.iloc[0,:])


# data_expand= pd.DataFrame.from_dict(data, orient='columns')



