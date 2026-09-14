function f(text, prefix){
    if (text.startsWith(prefix)){
        return text.slice(prefix.length);
    }
    if (text.includes(prefix)){
        return text.replace(prefix, '').trim();
    }
    return text.toUpperCase();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("abixaaaily", "al"),"ABIXAAAILY");
}

test();
