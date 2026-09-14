function f(value){
    var parts = value.split(' ').filter(function(_, index) {
        return index % 2 === 0;
    });
    return parts.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("coscifysu"),"coscifysu");
}

test();
