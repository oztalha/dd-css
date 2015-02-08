# DD-CSS
---------
## Data-driven Computational Social Science

[DD-CSS](http://dd-css.com) is an open source web application that helps collecting data from social media platforms such as Twitter, and analyze them.
It is powered by Flask, a highly modular microframework for Python.
DD-CSS is initiated by [Talha Oz][toz].

In this project I highly benefitted from the books [Mining the Social Web](https://github.com/ptwobrussell/Mining-the-Social-Web-2nd-Edition) and [Flask Web Development](https://github.com/miguelgrinberg/flasky).

## Features
-----------
### Twitter
* Obtain an OAuth access token on behalf of a Twitter user
* Get the friends/followers list of a user as JSON/CSV file
* Get last 3200 tweets of a user in JSON/CSV format
* Get IDs as well as many other information on the members of a Twitter list in JSON/CSV format

## Installation
---------------
### MongoDB
After installing MongoDB, there is no need to create db or collection. The only configuration is to ensure indexing.
* Index the queries by db.queries.ensureIndex({username:1, created_time:1, qname:1})
 
[toz]: http://talhaoz.com
