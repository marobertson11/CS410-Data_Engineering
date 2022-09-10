# CS410 Data Engineering

Current Completions:

Week 2 in-class activities (Python) 
Week 3 in-calss Activities (producer.py)
Week 4 in-class Activities (Jupiter Python Notebook and pdf)
Week 5 in-class Activities 
Week 6 in-class Activities
Week 7 in-class Activities (Jupiter Python Notebook)
Week 8-9 In-class Activites 

Main Project
    run.sh: This is the bash program that will run at the beginning of each morning. 
    
    gatherData.py: Python program designed to access websites, gather data, convert and clean (if necessary) into a json file
    
    data_producer.py: Python program that is designed to access the json file created by the gatherData.py and send it through to Kafka to be consumed later. 
    
    data_consumer.py: Python program designed to access the messages that were produced. When accessed, it each message will undergo a series of verifications that it has the necessary information. If it does, then it will be consumed and have its contents be broken into 2 differrent arrays. These arrays will be sent to the PostgreSQL table that is assigned to, based on its information.
    
    server.py: This program will create a server that will allow the user to display the map that was created via tsvscript.py
    
    topic_clean.py: Designed to go through the Kafka topic that is provided in code and remove all entries withough sending messages to the server
    
    tsvscript.py: This program will take a tsv document and convert it into a geojson that will be able to be readable for the server.py.
    
    website-producer.py: This will gather the data that was gathered from the Event Stop website and preform the producer actions.
    
    website-consumer.py: This will consume the data that was provided from the website-producer.py. It will go through a series of checks to determine if the information has the relevant information and also determine if this information has already been entered as of yet. If it has been entered or does not have the necessary information, then it will be skipped. If it new and complete information, it will be sent to the PostgreSQL tables.
    
    
    Project Part 1: This was the first assignment that displayed the basic  information that was gathered within the first section of the project. This includes the day of the week and date of the record, the time that this information was accessed, the number of sensor readings that were preformed for this day's record, size of the the data, and the number of kafka messages that were produced. 
    
    Project Part 2: This part of the project was designed to incoperate data, after it has gone through transformations, that was previously gathered and insert it into 2 PostgreSQL tables. One table (named Breadcrumb) states the date and time, latitude, longitude, the direction it was going, the speed at the time of the record, and its trip_id of all accepted records for all collected days. The second table, named Trip, states the trip_id, the route_id, the vehicle_id, the service_key (which means if it is a weekday, Saturday, or Sunday), and the 'direction' (if it was coming from its starting point or going to the original starting point). The Trip table, at the time, was not complete as the was missing information to properly fill it in. On this document, there is a table that states the day of the entry, what day of the week it is, number of sensor readings that were preformed, and the number of accepted submittions into the PostgreSQL tables. There are also example queries at the end of the document. 
    
    Project Part 3: This part of the project was designed to add the information that was missing from the Trip table. This section requrired new a new producer, a consumer, and the gatherData.py to be changed to incoperate the new website to gather the information from. Once the data was gathered, converted into a json file, sent through the producer, it was sent to the consumer to preform data validation/transformation. If the information passed the test, it was sent to the Trip table. The last part of this part was to utilize the data that was given to create visualizations that would demonstrate  the records of the vehicles with any given query. This was done with the MapboxGL. 
