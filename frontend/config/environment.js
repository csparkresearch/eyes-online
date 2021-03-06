/* eslint-env node */
'use strict';

module.exports = function(environment) {
  let ENV = {
    modulePrefix: 'eyes-online',
    environment,
    rootURL: '',
    locationType: 'hash',
    EmberENV: {
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. 'with-controller': true
      },
      EXTEND_PROTOTYPES: {
        // Prevent Ember Data from overriding Date.parse.
        Date: false
      }
    },

    APP: {
      // Here you can pass flags/options to your application instance
      // when it is created
	    API_HOST: 'http://127.0.0.1:8000',
    },
    cordova: {
      rebuildOnChange: false,
      emulate: false
     }

  };


switch (environment) {
	case 'development':
		ENV.APP.usingCors = true;
		ENV.APP.corsWithCreds = true;
		ENV.APP.apiURL = 'http://localhost:8000'
		break;
	case 'production':
		ENV.APP.usingCors = true;
		ENV.APP.corsWithCreds = true;
		ENV.APP.apiURL = 'https://eyes-online.herokuapp.com'
		break;
	case 'eyes-test':
		ENV.APP.usingCors = true;
		ENV.APP.corsWithCreds = true;
		ENV.APP.apiURL = 'https://eyes-test.herokuapp.com'
		break;
	case 'test':
		ENV.locationType = 'none';
		// keep test console output quieter
		ENV.APP.LOG_ACTIVE_GENERATION = false;
		ENV.APP.LOG_VIEW_LOOKUPS = false;

		ENV.APP.rootElement = '#ember-testing';
		break;
}


  return ENV;
};
