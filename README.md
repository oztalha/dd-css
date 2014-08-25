# DD-CSS
---------
## Data-driven Computational Social Science

DD-CSS is an effort to build new computational tools to help collect and analyze social media data.
It is powered by Flask, a highly modular microframework for Python, to encourage other developers to contribute to this project.

There is a growing interest in mining the social web by so many professions for different purposes.
So, while many parties may benefit from DD-CSS, our primary target is computational social scientists.
We would like you to import your collection & analysis methods into DD-CSS especially if you are publishing in [social computing conferences](http://www.mli.gmu.edu/toz/wordpress/2014/05/26/social-computing-conferences/).


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
* db.queries.ensureIndex({username:1, created_time:1, qname:1})
