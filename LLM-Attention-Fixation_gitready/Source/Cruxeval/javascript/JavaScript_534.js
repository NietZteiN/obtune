function f(sequence, value){
    let i = Math.max(sequence.indexOf(value) - Math.floor(sequence.length / 3), 0);
    let result = '';
    for (let j = 0; j < sequence.slice(i).length; j++) {
        let v = sequence[i + j];
        if (v === '+') {
            result += value;
        } else {
            result += sequence[i + j];
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("hosu", "o"),"hosu");
}

test();
