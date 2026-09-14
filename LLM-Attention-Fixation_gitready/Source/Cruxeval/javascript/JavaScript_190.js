function f(text){
    let short = '';
    for(let c of text){
        if(c === c.toLowerCase() && isNaN(c)){
            short += c;
        }
    }
    return short;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("980jio80jic kld094398IIl "),"jiojickldl");
}

test();
