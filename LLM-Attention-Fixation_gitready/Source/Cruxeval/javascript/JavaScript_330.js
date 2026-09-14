function f(text){
    let ans = [];
    for(let i = 0; i < text.length; i++){
        if(!isNaN(parseInt(text[i]))){
            ans.push(text[i]);
        } else {
            ans.push(' ');
        }
    }
    return ans.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("m4n2o")," 4 2 ");
}

test();
