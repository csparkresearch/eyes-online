import Ember from 'ember';

const { $, $: { post, extend }, Controller, get } = Ember;

export default Controller.extend({
  editTitle        : 'myFile',
/* ---- Add Script Screen ---*/
  inputDescription : '',
  submitFailed     : false,
  failedMessage    : 'Failed to Login',
  updateDone       : false,
  updateMessage    : 'updated successfully',
  isProcessing     : false,
  isSlowConnection : false,
  timeout          : null,
  clearTimer       : null,
  openCodeId       : null,
  fetchedCode      : null,
  editorContents   : '',
  deleteScriptId   : 0,
  deleteScriptName : '',
  viewModalTitle   : '',
  viewContents     : '',
  viewAceInit(editor) {
    editor.setHighlightActiveLine(false);
    editor.setShowPrintMargin(false);
    editor.getSession().setTabSize(2);
    editor.getSession().setMode('ace/mode/python');
    editor.setReadOnly(true);
  },

  reset() {
    clearTimeout(this.get('timeout'));
    this.setProperties({
      submitFailed     : false,
      updateMessage    : 'updated successfully',
      updateDone       : false,
      isProcessing     : false,
      isSlowConnection : false
    });
  },
  success(response) {
    this.reset();
    if (response.status) {
      this.setProperties({
        updateDone    : true,
        updateMessage : 'updated successfully',
        clearTimer    : setTimeout(this.clearUpdateMessage.bind(this), 1000)
      });
    }    else {
      this.set('submitFailed', true);
      this.failedMessage = String(response.message);
    }
  },

  // Editing your submitted scripts

  fetchedCodeSuccess(response) {
    this.reset();
    if (response.status) {
      this.setProperties({
        updateMessage    : 'Retrieved from server',
        updateDone       : true,
        clearTimer       : setTimeout(this.clearUpdateMessage.bind(this), 1000),
        editorContents   : response.Code,
        inputDescription : response.Code,
        inputTitle       : response.Filename
      });
    }    else {
      this.set('submitFailed', true);
      this.failedMessage = String(response.message);
    }
  },
  clearUpdateMessage() {
    this.set('updateDone', false);
  },
  error() {
    this.reset();
    this.set('submitFailed', true);
    this.set('failedMessage', 'Submission failed. Server down? ');
  },
  failure(response) {
    this.reset();
    this.set('submitFailed', true);
    if (response.hasOwnProperty('message')) {
      this.set('failedMessage', response.message);
    } else {
      this.set('failedMessage', 'Transaction failed. App Error. ');
    }
  },
  slowConnection() {
    this.set('isSlowConnection', true);
  },

  actions: {
    openEditModal(script) {
      this.reset();
      this.openCodeId = script.Id;
      post('/getScriptById', { 'id': script.Id }, this, 'json')
        .then(this.fetchedCodeSuccess.bind(this), this.failure.bind(this), this.error.bind(this));
      $('#editModal').modal();
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
      post('/updateScript', extend({}, this.getProperties('inputTitle', 'inputDescription'), { 'codeId': this.openCodeId }), this, 'json')
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
