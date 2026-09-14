function f(text, value){
    let ls = text.split('');
    if (ls.filter(x => x === value).length % 2 === 0) {
        while (ls.includes(value)) {
            ls.splice(ls.indexOf(value), 1);
        }
    } else {
        ls = [];
    }
    return ls.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("abbkebaniuwurzvr", "m"),"abbkebaniuwurzvr");
}

test();
