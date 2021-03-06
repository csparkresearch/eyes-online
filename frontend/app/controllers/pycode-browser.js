import Ember from 'ember';
import config from '../config/environment';

const { Controller, $: { get, post }, $ } = Ember;

export default Controller.extend({
  apiURL            : config.APP.apiURL,
  doctitle          : 'documentation',
  viewScriptName    : 'loading ...',
  viewScriptContent : '',
  activatedFilename : '',
  scriptdata        : {},
  codeResults       : '',

  fetchedCodeSuccess(response) {
    if (response.status) {
      $('.teal.indicating').progress('complete');
      this.set('scriptdata', response.staticdata);
    }
  },

  actions: {
    viewScript(path, filename) {
      $('.viewmodal.modal').modal('show');
      $('.ui.dimmer.viewmodalloading').addClass('active');
      get(this.apiURL + '/' + path + '/' + filename)
        .then(response => {
          this.setProperties({
            viewScriptName    : filename,
            viewScriptContent : response// .replace(/(?:\r\n|\r|\n)/g, '<br>').replace(/(?:\s\s)/g, '&nbsp;')
          });
          $('.ui.dimmer.viewmodalloading').removeClass('active');
        });
    },
    runScript(path, filename) {
      $('.ui.menu').find('.item').tab('change tab', 'run');
      $('.ui.dimmer.runmodalloading').addClass('active');
      this.set('activatedFilename', filename);
      post('/runScriptByFilename', { 'path': path, 'filename': filename }, this, 'json')
        .then(response => {
          this.setProperties({
            codeResults: response.result
          });
          $('.ui.dimmer.runmodalloading').removeClass('active');
        });
        

    },
    getStaticScripts() {
      get({
        xhr() {
          var xhr = new window.XMLHttpRequest();
          xhr.upload.addEventListener('progress', function(evt) {
            if (evt.lengthComputable) {
              console.log('length up:', evt.total);
              $('.teal.indicating').progress('set percent', 100 * evt.loaded / evt.total);
              // context.set('progressOne', 100 * evt.loaded / evt.total);
            } else {
              console.log('length no computable. u');
            }
          }, false);

          xhr.addEventListener('progress', function(evt) {
            if (evt.lengthComputable) {
              console.log('length down:', evt.total);
              $('.teal.indicating').progress('set percent', 100 * evt.loaded / evt.total);
              // context.set('progressOne', 100 * evt.loaded / evt.total);
            } else {
              console.log('length not computable. d');
            }
          }, false);
          return xhr;
        },
        context  : this,
        type     : 'GET',
        url      : '/getStaticScripts',
        dataType : 'json',
        success  : this.fetchedCodeSuccess.bind(this)
      });
    },

    updateScript() {
      this.setProperties({
        submitFailed  : false,
        failedMessage : '',
        isProcessing  : true
      });
      this.set('timeout', setTimeout(this.slowConnection.bind(this), 1000));
      post('/updateScript', Controller.extend({}, this.getProperties('inputTitle', 'inputDescription'), { 'codeId': this.openCodeId }), this, 'json')
        .then(this.success.bind(this), this.failure.bind(this), this.error.bind(this));
    },
    showDeleteDialog(script) {
      this.set('deleteScriptId', script.Id);
      this.set('deleteScriptName', script.Filename);
      $('#deleteModal').modal();
    },
    deleteScript() {
      post('/deleteScript', { 'scriptId': this.deleteScriptId }, this, 'json');
      $('#deleteModal').modal('hide');
      this.send('refresh');
    }

  }

});
