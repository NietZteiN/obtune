function f(text, value){
    let indexes = [];
    for(let i = 0; i < text.length; i++){
        if(text[i] === value){
            indexes.push(i);
        }
    }
    let new_text = text.split('');
    indexes.sort((a, b) => b - a); // reverse sort to avoid index shifting issue
    for(let i of indexes){
        new_text.splice(i, 1);
    }
    return new_text.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("scedvtvotkwqfoqn", "o"),"scedvtvtkwqfqn");
}

test();
