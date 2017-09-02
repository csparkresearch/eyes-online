/* eslint-env node */
'use strict';

const EmberApp = require('ember-cli/lib/broccoli/ember-app');

module.exports = function(defaults) {
  let app = new EmberApp(defaults, {
    // Add more options here
    ace: {
      themes  : ['cobalt', 'ambiance', 'chaos'],
      modes   : ['python', 'javascript'],
      workers : ['javascript']
    }
  });

  app.import('vendor/gallery.js');

  app.import('bower_components/bootstrap/dist/js/bootstrap.min.js');
  app.import('bower_components/bootstrap/dist/css/bootstrap.min.css');
  app.import('bower_components/bootstrap/dist/css/bootstrap.min.css.map');

  app.import('bower_components/bootstrap/dist/css/bootstrap-theme.min.css');
  app.import('bower_components/bootstrap/dist/fonts/glyphicons-halflings-regular.woff2', {  destDir: 'fonts'  });

  return app.toTree([]);
};
