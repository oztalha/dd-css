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

### Facebook
* Obtain an OAuth access token on behalf of a Facebook user
* Get the number of shares of a url

## Installation
---------------
### MongoDB
* Index the queries by db.queries.ensureIndex({username:1, created_time:1, qname:1})
