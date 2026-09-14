function f(seq, value){
    let roles = {};
    seq.forEach(item => {
        roles[item] = 'north';
    });
    if (value) {
        value.split(', ').forEach(key => {
            roles[key.trim()] = 'north';
        });
    }
    return roles;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["wise king", "young king"], ""),{"wise king": "north", "young king": "north"});
}

test();
