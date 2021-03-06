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
    },
    SemanticUI: {
      import: {
        fonts: false,
        images: false
      }
    }
  });

  app.import('vendor/gallery.js');

  app.import('bower_components/woofmark/dist/woofmark.min.js');
  app.import('bower_components/domador/dist/domador.min.js');
  app.import('bower_components/megamark/dist/megamark.min.js');

  app.import('bower_components/jqplot/jquery.jqplot.min.js');
  app.import('bower_components/jqplot/plugins/jqplot.cursor.js');
  app.import('bower_components/jqplot/plugins/jqplot.highlighter.js');
  app.import('bower_components/jqplot/plugins/jqplot.pointLabels.js');

  app.import('bower_components/jqplot/jquery.jqplot.min.css');

  return app.toTree([]);
};
