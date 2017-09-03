import Ember from 'ember';

const { Route, $: { getJSON } } = Ember;

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
    refresh() {
      this.refresh();
    }
  }
});
