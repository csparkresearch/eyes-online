import Ember from 'ember';

const { $, Component } = Ember;

export default Component.extend({
  didInsertElement() {
    $.jqplot(this.data.name, this.data.data, this.data.style);
  }
});
