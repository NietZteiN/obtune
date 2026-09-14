function f(s){
    let count = {};
    for(let i = 0; i < s.length; i++){
        let char = s[i].toLowerCase();
        if(s[i] === s[i].toLowerCase()){
            count[char] = s.split(char).length - 1 + (count[char] || 0);
        } else {
            count[char] = s.split(s[i].toUpperCase()).length - 1 + (count[char] || 0);
        }
    }
    return count;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("FSA"),{"f": 1, "s": 1, "a": 1});
}

test();
