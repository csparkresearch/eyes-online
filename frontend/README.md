# ExpEYES Online

ExpEYES online is an online doc and app store for expeyes.
This is only a webapp to deal with the [API server](eyes-online.herokuapp.com)

## Prerequisites to test locally

### Dependencies :

* [Git](https://git-scm.com/)
* [Node.js](https://nodejs.org/) (with NPM)
* [Ember CLI](https://ember-cli.com/)

## Installation

* `git clone https://github.com/csparkresearch/eyes-online`
* `cd frontend`
* `npm install`
* `bower install`

## Running / Development

set the DATABASE_URL environment variable to point to your database
`export DATABASE_URL=postgres:///eyes_db`

### Start the API server
`gunicorn app:app`

### Start the Webapp
`ember serve`

Visit the webapp app at [http://localhost:4200](http://localhost:4200).
Visit the API server at [http://localhost:4000](http://localhost:4000) to check out the API docs
