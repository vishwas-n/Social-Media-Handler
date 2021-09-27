# Social-Media-Handler
## DS Project. One place to manage them all (all social media accounts)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

##### This Project aims to build a one-stop application to manage multiple social media accounts viz. Twitter, Facebook, Instagram. For phase 1, the end-to-end work flow for Twitter is implemented for simple use-case of search i.e search for a given keyword.

**Design:**

 1. **Server:** This is a flask application deployed as a docker container. It contains the logic for handling the user query and processing it appropriately. In online mode, data is fetched from the social media APIs and in offline mode, data is fetched from the Solr data Store. Note that, only the data fetched from online APIs previously is pushed into SOLR and only those keywords can be fetched in offline mode.

 2. **Client:** A flask application using Python, which creates a basic UI for the user to enter their inputs. This application is deployed as a docker container. The user input is internally passed to server using a GET Request with the options entered in UI as a payload.

 3. **Database:** Solr NoSQL store deployed as a docker container, to index and store user query keywords and their corresponding tweets. This indexed data can be accessed from the DB by querying using the Keyword. The server will push data into Solr along with the user entered keyword and in offline mode the server fetches directly from this DB.

![DS Architecture](https://github.com/vishwas-n/Social-Media-Handler/blob/main/DS%20Architecture.png)


**Commands to Deploy:
**
1) Start the Server, by giving the command : Docker compose
2) Start the Client in another terminal, by giving the command : Docker run up
3) Go to localhost:8983, and check if Solr is running.
4) Go to localhost:5000, and check if Client is running.
5) In localhost:5000, select appropriate values for the input boxex. For example, select 'Twitter' for Social Media, 'Covid' for Keyword & 'Online' for mode type. After selecting this, click 'Submit'.
6) The results related to the Keyword will now be displayed on the right side of the web page. The result set can be scrolled through to access the various responses received from Twitter.
7) Go to localhost:8983, to access Solr. Click on Query to verify the presence of data in the DB.
8) Stop the Server. Now again go to Solr, and verify the presence of data.
9) Start the Server again, and go to localhost:5000 again. This time try any example with Offine mode. For example, Twitter, Sample, Offline. If tweets for the Keyword 'Sample' aren't available in the DB, no results will show up. If this happens, run the same example with Online. This will fetch new tweets for the keyword, and index it in the Solr DB. 
10) Now you can come back and again try the example in the previous step (i.e) Twitter, Sample, Offline. Since there is data for the Keyword now in the DB, results will get populated.
11) Go to localhost:8983, to access Solr. Click on Query to verify the presence of this data (Sample) and the previous data (Covid) indexed in the DB.
