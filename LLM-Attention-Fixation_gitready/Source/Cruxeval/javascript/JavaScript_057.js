function f(text){
    text = text.toUpperCase();
    let count_upper = 0;
    for(let i = 0; i < text.length; i++){
        let char = text.charAt(i);
        if(char === char.toUpperCase()){
            count_upper++;
        } else {
            return 'no';
        }
    }
    return Math.floor(count_upper / 2);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ax"),1);
}

test();
