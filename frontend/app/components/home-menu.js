import Ember from 'ember';

const { $: { post }, Component, inject, $ } = Ember;

export default Component.extend({
/* ---- Login Screen ---*/
  routing            : inject.service('-routing'),
  loginFailed        : false,
  loginFailedMessage : 'Failed to Login',
  isProcessing       : false,
  isSlowConnection   : false,
  timeout            : null,

  success(response) {
    this.reset();
    if (response.status) {
      this.reset();
      this.sendAction('signin');
      $('.loginmodal.modal').modal('hide');
      // get('routing').transitionTo('user-home');
    }    else {
      this.set('loginFailed', true);
      this.loginFailedMessage = String(response.message);
    }
    
  },
  error() {
    this.reset();
    this.set('loginFailed', true);
    this.set('loginFailedMessage', 'Sign-In failed. Server down? ');
  },
  failure() {
    this.reset();
    this.set('loginFailed', true);
    this.set('loginFailedMessage', 'Sign-In failed. App Error. ');
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

    logMeIn() {
      this.setProperties({
        loginFailed        : false,
        loginFailedMessage : '',
        isProcessing       : true
      });

      this.set('timeout', setTimeout(this.slowConnection.bind(this), 1000));
      post('/validateLogin', { 'inputEmail': this.get('loginEmail'), 'inputPassword': this.get('loginPassword') }, this, 'json')
        .then(this.success.bind(this), this.failure.bind(this), this.error.bind(this));
    }

  },
  didInsertElement() {
    // fix menu when passed
    $('.masthead')
      .visibility({
        once: false,
        onBottomPassed: function() {
          $('.fixed.menu').transition('fade in');
        },
        onBottomPassedReverse: function() {
          $('.fixed.menu').transition('fade out');
        }
      })
    ;

    // create sidebar and attach to menu open
    // $('.ui.sidebar')
    //   .sidebar('attach events', '.toc.item')
    // ;

    $('.loginmodal.modal')
      .modal('attach events', '.loginmodal.button', 'show')
    ;

  }

});
