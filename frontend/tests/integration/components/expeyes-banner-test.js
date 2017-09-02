import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('expeyes-banner', 'Integration | Component | expeyes banner', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{expeyes-banner}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#expeyes-banner}}
      template block text
    {{/expeyes-banner}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
