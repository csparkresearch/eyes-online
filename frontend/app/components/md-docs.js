import Ember from 'ember';

const { Component } = Ember;

export default Component.extend({
  rfence: /(^|\s)md-lang-((?:[^\s]|$)+)/,

  parseHTML(value, options) {
    return domador(value, {
      fencing         : true,
      fencinglanguage : this.fences,
      markers         : options.markers
    });
  },

  fences(el) {
    var match = el.firstChild.className.match(this.rfence);
    if (match) {
      return match.pop();
    }
  },

  didInsertElement() {
    woofmark(document.querySelector('#woof'), {
      parseMarkdown : megamark,
      parseHTML     : this.parseHTML,
      defaultMode   : 'markdown',
      fencing       : true,
      wysiwyg       : false
    });
  }
});
