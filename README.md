# Online docs and application manager

[API server hosted on Heroku](https://eyes-online.herokuapp.com/) : The dyno is reaped after half an hour of inactivity, and can take up to 10 seconds to wak up and respond to the first request .
[ExpEYES Website](http://expeyes.in)

### Running this locally

Install Python dependencies from requirements.txt
Create a postgresql dependency. e.g. `postgres:///eyes_db`

set the DATABASE_URL environment variable to point to your database

`export DATABASE_URL=postgres:///eyes_db`

launch the app 

`gunicorn app:app`

Now navigate to `localhost:8000` in order to view the landing page and API docs

### API Docs

API documents are displayed with swagger-ui . Flasgger is used to set it up.

`localhost:8000/apidocs` lets you test the API from the browser itself

You may also use simple Python scripts, or [Postman](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en) chrome extension to test the API endoints. P.S. Swagger APIdocs are a lot easier to use, and are configured to accept the right arguments.


### Frontend

None exists at this point. Plan to make an ember-js based application when time is available


