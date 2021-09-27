# Social-Media-Handler
DS Project. One place to manage them all (all social media accounts)

This Project aims to build a one-stop application to manage multiple social media accounts viz. Twitter, Facebook, Instagram. For phase 1, the end-to-end work flow for Twitter is implemented for simple use-case of search i.e search for a given keyword.

**Design:
**
Server: It is a docker that contains the logic for handling the user query, and the Database as separate images. 
Client: A flask application using Python, which creates a basic UI for the user to enter their inputs. This application is created as a docker.
Database: Used Solr docker, to index and store user query keywords and their corresponding tweets. This indexed data can be accessed from the DB by querying using the Keyword.

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
