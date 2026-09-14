function f(multi_string){
    let cond_string = multi_string.split(' ').map(word => word.split('').every(char => char.charCodeAt(0) < 128));
    if (cond_string.includes(true)) {
        return multi_string.split(' ').filter(word => word.split('').every(char => char.charCodeAt(0) < 128)).join(', ');
    }
    return '';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("I am hungry! eat food."),"I, am, hungry!, eat, food.");
}

test();
