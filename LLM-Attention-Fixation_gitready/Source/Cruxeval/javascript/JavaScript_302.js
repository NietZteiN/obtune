function f(string){
    return string.replace('needles', 'haystacks');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("wdeejjjzsjsjjsxjjneddaddddddefsfd"),"wdeejjjzsjsjjsxjjneddaddddddefsfd");
}

test();
