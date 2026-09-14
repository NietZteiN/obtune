function f(text, size){
    let counter = text.length;
    for(let i = 0; i < size - size % 2; i++){
        text = ' ' + text + ' ';
        counter += 2;
        if(counter >= size){
            return text;
        }
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("7", 10),"     7     ");
}

test();
