import Ember from 'ember';
import config from '../config/environment';

const { Controller } = Ember;

export default Controller.extend({
  apiURL         : config.APP.apiURL,
  doctitle       : 'documentation'
});
