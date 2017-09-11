import Ember from 'ember';
import config from '../config/environment';

const { Controller, $: { get, post }, $ } = Ember;

export default Controller.extend({
  apiURL      : config.APP.apiURL,
  doctitle    : 'documentation',
  scriptdata  : {},
  fetchedCodeSuccess(response) {
    if (response.status) {
      $('.teal.indicating').progress('complete');
      this.set('scriptdata', response.staticdata);
    }
  },
  actions: {
    getStaticScripts() {
      get({
        xhr() {
          var xhr = new window.XMLHttpRequest();
          xhr.upload.addEventListener('progress', function(evt) {
            if (evt.lengthComputable) {
              $('.teal.indicating').progress('update progress', 100 * evt.loaded / evt.total );
              // context.set('progressOne', 100 * evt.loaded / evt.total);
            }
          }, false);

          xhr.addEventListener('progress', function(evt) {
            if (evt.lengthComputable) {
              $('.teal.indicating').progress('update progress', 100 * evt.loaded / evt.total );
              //context.set('progressOne', 100 * evt.loaded / evt.total);
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
    openViewModal(script) {
      $('#viewModal').modal();
      post('/getScriptByFilename', { 'Filename': script.Filename }, this, 'json')
        .then(response => {
          if (response.status) {
            this.setProperties({
              viewContents   : response.Code,
              viewModalTitle : response.Filename
            });
          } else {
            this.set('viewModalTitle', 'Could not retrieve script!');
          }
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
