# Social-Media-Handler
## DS Project. One place to manage them all (all social media accounts)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

##### This Project aims to build a one-stop application to manage multiple social media accounts viz. Twitter, Facebook, Instagram. For phase 1, the end-to-end work flow for Twitter is implemented for simple use-case of search i.e search for a given keyword.

**Design:**

 1. **Server:** This is a flask application deployed as a docker container. It contains the logic for handling the user query and processing it appropriately. In online mode, data is fetched from the social media APIs and in offline mode, data is fetched from the Solr data Store. Note that, only the data fetched from online APIs previously is pushed into SOLR and only those keywords can be fetched in offline mode.

 2. **Client:** A flask application using Python, which creates a basic UI for the user to enter their inputs. This application is deployed as a docker container. The user input is internally passed to server using a GET Request with the options entered in UI as a payload.

 3. **Database:** Solr NoSQL store deployed as a docker container, to index and store user query keywords and their corresponding tweets. This indexed data can be accessed from the DB by querying using the Keyword. The server will push data into Solr along with the user entered keyword and in offline mode the server fetches directly from this DB.

All containers are made visible to one another using docker networks. Steps to run the server and client apps are given below.

![DS Architecture](https://github.com/vishwas-n/Social-Media-Handler/blob/main/DS%20Architecture.png)


**Commands to Deploy:**

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

3) Go to the Client folder and build a docker image using the given Dockerfile. This will bundle all the code and create an flask application client image. Then run it using docker run and also attach it to the earlier created network. Run the below command
```sh
docker build . --tag docker_flask_client_image
```
```sh
docker run --publish 5000:5000 --net server_default --name docker_flask_client docker_flask_client_image
```
4) Now, the server which is running as a container is mapped to the localhost port 8990 and the client which is running as a container is mapped to localhost port 5000. The solr is mapped to port 8983. 



7) In localhost:5000, select appropriate values for the input boxex. For example, select 'Twitter' for Social Media, 'Covid' for Keyword & 'Online' for mode type. After selecting this, click 'Submit'.
8) The results related to the Keyword will now be displayed on the right side of the web page. The result set can be scrolled through to access the various responses received from Twitter.
9) Go to localhost:8983, to access Solr. Click on Query to verify the presence of data in the DB.
10) Stop the Server. Now again go to Solr, and verify the presence of data.
11) Start the Server again, and go to localhost:5000 again. This time try any example with Offine mode. For example, Twitter, Sample, Offline. If tweets for the Keyword 'Sample' aren't available in the DB, no results will show up. If this happens, run the same example with Online. This will fetch new tweets for the keyword, and index it in the Solr DB. 
12) Now you can come back and again try the example in the previous step (i.e) Twitter, Sample, Offline. Since there is data for the Keyword now in the DB, results will get populated.
13) Go to localhost:8983, to access Solr. Click on Query to verify the presence of this data (Sample) and the previous data (Covid) indexed in the DB.
