function f(text, prefix){
    while(text.startsWith(prefix)){
        text = text.slice(prefix.length) || text;
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ndbtdabdahesyehu", "n"),"dbtdabdahesyehu");
}

test();
