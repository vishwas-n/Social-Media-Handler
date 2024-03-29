# Social-Media-Handler
## Distributed, Asynchronous Publish Subscribe system to handle subscriptions for social media data (Twitter, Reddit).

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

##### This Project aims to build a one-stop application to manage multiple social media accounts viz. Twitter, Facebook, Instagram. For phase 1, the end-to-end work flow for Twitter is implemented for simple use-case of search i.e search for a given keyword.

## **Design:**

 1. **Server:** This is a flask application deployed as a docker container. It contains the logic for handling the user query and processing it appropriately. In online mode, data is fetched from the social media APIs and in offline mode, data is fetched from the Solr data Store. Note that, only the data fetched from online APIs previously is pushed into SOLR and only those keywords can be fetched in offline mode.

 2. **Client:** A flask application using Python, which creates a basic UI for the user to enter their inputs. This application is deployed as a docker container. The user input is internally passed to server using a GET Request with the options entered in UI as a payload.

 3. **Database:** Solr NoSQL store deployed as a docker container, to index and store user query keywords and their corresponding tweets. This indexed data can be accessed from the DB by querying using the Keyword. The server will push data into Solr along with the user entered keyword and in offline mode the server fetches directly from this DB.

All containers are made visible to one another using docker networks. Steps to run the server and client apps are given below.

![DS Architecture](https://github.com/vishwas-n/Social-Media-Handler/blob/main/DS%20Architecture.png)


## **Dataflow:**

1. Once the server is started, a REST api is exposed to utilize its functionaly. The server currently supports a GET request with payload taking the params.
2. The Client webpage has multiple input options. This input is captured and translated to a GET request with payload. 
3. The server expects this **payload** in the GET api of following endpoint ```(http://127.0.0.1:8990/social_media_handle)```
```
    {
     "socialmedia": "twitter",
     "keyword": "covid",
     "fetchmode": "online"
    }
```
4. Furthermore, the server processes this payload and either hits the live social media apis or SOLR fetch api and returns the appropriate response. In case of live mode, the data from social media apis is ingested to SOLR DB before returning this as response.


## **Features:**

1. Understanding the options on the webpage:
     - Social Media Type (Dropdown): Twitter, Facebook, Instagram. Twitter end-to-end flow is implemented for phase 1. This will be extended to other social media platforms in next phase.
     - Keyword (Textbox): The keyword to search for in any of the above social media. For e.g. if 'covid' is given as the keyword, top tweets related to 'covid' will be fetched and displayed.
     - FetchMode (Radio-buttons): **Online & Offline**
           
         **Online Mode**: The keyword is searched for using the selected social media live api. The data that is return by this api is processed and ingested into SOLR DB. The same is returned to the webpage display.
           
         **Offline Mode**: The keyword is searched directly in the SOLR DB (without hitting any of the live apis). So only if the data for the keyword was previously ingested, results will show up in this mode. Otherwise, the response will be 'No Data Found'.
       
2. Independent Containers:
     - The Server, Client, SOLR DB are running as separate containers. So even if the server stops/crashes, there is no data loss as the data is already persisted in SOLR DB, which would still be running as a separate container. If Client app stops/crashes, just a restart of Client will suffice.

3. Proper Abstraction of Data Flow:
     - The Client does not have direct access to the SOLR DB and would have to go through the Server only to fetch data from SOLR DB.

4. Simple/Lightweight UI:
     - The webpage has been developed using Flask to make it lightweight and user-friendly. Currently, the list of tweets will be diplayed in a scrollable fashion.


## **Commands to Deploy:**

1) Create a docker network which will be used by all the containers. Run the below command 
```sh
docker network create server_default
```
   This creates a network with name server_default
   
   
2) Start the SOLR DB by pulling its image from docker hub. Run the below command to fire it up. (Note: SOLR needs a core to be created before pushing data, this command will precreate a core required to ingest data). Start it by attaching to the above network.
```sh
docker run --publish 8983:8983 --net server_default --name solr solr solr-precreate base_core
```

3) Go to the Server folder and build a docker image using the given Dockerfile. This will bundle all the code and create an flask application server image. Then run it using docker run and also attach it to the earlier created network. Run the below command
```sh
docker build . --tag docker_flask_server_image
```
```sh
docker run --publish 8990:8990 --name docker_flask_server --net server_default docker_flask_server_image
```

4) Go to the Client folder and build a docker image using the given Dockerfile. This will bundle all the code and create an flask application client image. Then run it using docker run and also attach it to the earlier created network. Run the below command
```sh
docker build . --tag docker_flask_client_image
```
```sh
docker run --publish 5000:5000 --net server_default --name docker_flask_client docker_flask_client_image
```

5) Now, the server which is running as a container is mapped to the localhost port 8990 and the client which is running as a container is mapped to localhost port 5000. The solr is mapped to port 8983. 

The application is live now and ready to play with.



## **Using the Application:**

1) Go to http://localhost:5000/ , select appropriate values for the input boxes. For example, select **'Twitter'** for Social Media (for phase 1, only twitter is integrated). Enter a value for keyword for e.g. 'Covid'. Choose the radio button 'Online' for fetch mode type. After selecting this, click 'Submit'. You'll be able to see 25 live tweets related to the entered keyword on the right side of the web page.

2) This data is persisted in SOLR along with the keyword. Go to http://localhost:8983/solr/#/base_core/query, to access Solr. Click on execute query at the bottom of the page to verify the presence of data in the SOLR DB.

3) Stop the Server. Now again go to Solr, and verify the presence of data. Also, if you try to execute from the client web page, it'll display server not found.

4) Start the Server again using docker start command
```sh
docker start docker_flask_server
```

5) Go to http://localhost:5000/ again. This time try any example with Offine mode. For example, Twitter, keyword = 'Sample', Offline. If tweets for the Keyword 'Sample' aren't available in the DB, no results will show up. If this happens, run the same example with Online. This will fetch new tweets for the keyword, and index it in the Solr DB. Once, the data is indexed, you can hit the api in 'Offline' mode. 

6) Now you can retry the example in the previous step (i.e) Twitter, Sample, Offline. Since there is data for the Keyword now in the DB, results will get populated. Also, hitting the api in 'Offline' mode for the earlier keyword fetched ('Covid') will return results too.
 
7) Go to http://localhost:8983/solr/#/base_core/query, to access Solr. Click on execute query to verify the presence of this data (for the new keyword 'Sample') and the previous data (Covid) indexed in the DB.
