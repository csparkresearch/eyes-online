# Online docs and application manager

+ [API server hosted on Heroku](https://eyes-online.herokuapp.com/) : The dyno is reaped after half an hour of inactivity, and can take up to 10 seconds to wake up and respond to the first request .
+ [API docs; by Swagger-UI](https://eyes-online.herokuapp.com/apidocs)
+ [Webapp built with EmberJS and Semantic-ui](https://eyes-online.surge.sh/#/pycode-browser)
+ [ExpEYES Website](http://expeyes.in)

### Running this locally

Install Python dependencies from requirements.txt

Create a postgresql database. e.g. `postgres:///eyes_db`
```
yourusername@host$ sudo -i -u postgres
postgres@host$ psql
postgres=# create database eyes_db with owner yourusername;
```

set the DATABASE_URL environment variable to point to your database

`export DATABASE_URL=postgres:///eyes_db`

launch the app 

`gunicorn app:app`

Now navigate to `localhost:8000` in order to view the landing page and API docs

## API Docs

API documents are displayed with swagger-ui . Flasgger is used to set it up.

`localhost:8000/apidocs` lets you test the API from the browser itself

You may also use simple Python scripts, or [Postman](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en) chrome extension to test the API endoints. P.S. Swagger APIdocs are a lot easier to use, and are configured to accept the right arguments.

![eyes-online-api](https://user-images.githubusercontent.com/19327143/30376286-4c29f2f8-98a9-11e7-80d6-261faae6c389.png)

## Frontend

A [frontend](https://eyes-online.surge.sh/#/pycode-browser) is being developed using EmberJS and semantic-ui
![eyes-online-pycode](https://user-images.githubusercontent.com/19327143/30376288-4c673334-98a9-11e7-868f-595fbac58cfc.png)

The frontend has also been packaged for android using cordova.

## Pycode-Browser

Code examples from [pycode-browser](https://github.com/sposh-science/pycode-browser) are also being served via the webapp. They can be viewed/downloaded at this point.



