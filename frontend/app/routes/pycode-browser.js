import Ember from 'ember';

const { Route, run, $ } = Ember;

export default Route.extend({
  actions: {
    didTransition(transition, originRoute) {
      run.next(this, 'initTabs');
      var controller = this.controllerFor('pycode-browser');
      controller.send('getStaticScripts');

    },
    refresh() {
      this.refresh();
    }
  },
  initTabs() {
    $('.menu .item').tab();
    $('.ui.sticky').sticky();
  }
});
