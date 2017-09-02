import Ember from 'ember';

const { Route, $: { getJSON } } = Ember;

export default Route.extend({
  model() {
    return getJSON('/getPublicScripts');
  },
  actions: {
    refresh() {
      this.refresh();
    }
  }
});
