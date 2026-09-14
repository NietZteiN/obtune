function f(s, separator){
    for(let i = 0; i < s.length; i++){
        if(s[i] === separator){
            let new_s = s.split('');
            new_s[i] = '/';
            return new_s.join(' ');
        }
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("h grateful k", " "),"h / g r a t e f u l   k");
}

test();
