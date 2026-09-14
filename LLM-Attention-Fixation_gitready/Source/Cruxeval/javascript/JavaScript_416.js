function f(text, old, replacement){
    let index = text.lastIndexOf(old, text.indexOf(old));
    let result = text.split('');
    while (index > 0) {
        result.splice(index, old.length, replacement);
        index = text.lastIndexOf(old, 0, index);
    }
    return result.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("jysrhfm ojwesf xgwwdyr dlrul ymba bpq", "j", "1"),"jysrhfm ojwesf xgwwdyr dlrul ymba bpq");
}

test();
