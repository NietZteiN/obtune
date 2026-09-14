function f(text){
    try {
        while (text.includes('nnet lloP')) {
            text = text.replace('nnet lloP', 'nnet loLp');
        }
    } finally {
        return text;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("a_A_b_B3 "),"a_A_b_B3 ");
}

test();
