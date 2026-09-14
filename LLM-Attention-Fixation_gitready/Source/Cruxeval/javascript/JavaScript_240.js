function f(float_number){
    let number = float_number.toString();
    let dot = number.indexOf('.');
    if (dot !== -1){
        return number.substring(0, dot) + '.' + number.substring(dot+1).padEnd(2, '0');
    }
    return number + '.00';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(3.121),"3.121");
}

test();
