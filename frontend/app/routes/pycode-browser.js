import Ember from 'ember';

const { Route, run, $: { getJSON }, $ } = Ember;

export default Route.extend({
  model() {
    return getJSON('/getStaticScripts');
  },
  actions: {
    didTransition() {
      run.next(this, 'initTabs');
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
