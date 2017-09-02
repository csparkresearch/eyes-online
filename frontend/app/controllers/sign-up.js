import Ember from 'ember';

const { $: { post }, Controller } = Ember;

export default Controller.extend({

/* ---- Sign Up Controller ---*/

  signUpFailed     : false,
  failedMessage    : 'Failed to Sign Up',
  isProcessing     : false,
  isSlowConnection : false,
  timeout          : null,

  success(response) {
    this.reset();
    if (response.status === true) {
      this.reset();
      this.transitionToRoute('index');
    }    else {
      this.set('signUpFailed', true);
      this.failedMessage = String(response.message);
    }
  },
  error() {
    this.reset();
    this.set('signUpFailed', true);
    this.set('failedMessage', 'Sign-Up failed. Server down? ');
  },
  failure() {
    this.reset();
    this.set('signUpFailed', true);
    this.set('failedMessage', 'Sign-Up failed. ? ');
  },
  slowConnection() {
    this.set('isSlowConnection', true);
  },
  reset() {
    clearTimeout(this.get('timeout'));
    this.setProperties({
      isProcessing     : false,
      isSlowConnection : false
    });
  },

  actions: {

    signMeUp() {
      this.setProperties({
        signUpFailed  : false,
        failedMessage : '',
        isProcessing  : true
      });

      this.set('timeout', setTimeout(this.slowConnection.bind(this), 100));
      post('/signUp', this.getProperties('inputName', 'inputEmail', 'inputPassword'), this, 'json')
        .then(this.success.bind(this), this.failure.bind(this), this.error.bind(this));
    }

  }

});

