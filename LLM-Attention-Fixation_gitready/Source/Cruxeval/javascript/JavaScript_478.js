function f(sb){
    let d = {};
    for(let i = 0; i < sb.length; i++){
        let s = sb[i];
        d[s] = (d[s] || 0) + 1;
    }
    return d;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("meow meow"),{"m": 2, "e": 2, "o": 2, "w": 2, " ": 1});
}

test();
