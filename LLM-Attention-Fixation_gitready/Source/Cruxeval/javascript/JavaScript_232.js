function f(text, changes){
    let result = '';
    let count = 0;
    changes = changes.split('');
    for(let char of text){
        result += (char === 'e') ? char : changes[count % changes.length];
        count += (char !== 'e') ? 1 : 0;
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("fssnvd", "yes"),"yesyes");
}

test();
