import Ember from 'ember';

const { Route, $: { getJSON } } = Ember;

export default Route.extend({
  model() {
    return getJSON('/getStaticScripts');
  },
  actions: {
    refresh() {
      this.refresh();
    }
  }
});
