import Ember from 'ember';

const { Route, run, $: { getJSON }, $} = Ember;

export default Route.extend({
  model() {
    return getJSON('/getPublicScripts');
  },
  actions: {
    error(reason) {
      if (reason.status === 404 || reason.status === 403) {
        return { 'status': false, 'data': {} };
      } else {
        return { 'status': false, 'data': {} };
      }
    },
    didTransition() {
      run.next(this, 'initTabs');
    },
    refresh() {
      this.refresh();
    }    
  },
  initTabs() {
    $('.menu .item').tab();
  }

});
