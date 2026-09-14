function f(text, splitter){
    return text.toLowerCase().split(' ').join(splitter);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("LlTHH sAfLAPkPhtsWP", "#"),"llthh#saflapkphtswp");
}

test();
