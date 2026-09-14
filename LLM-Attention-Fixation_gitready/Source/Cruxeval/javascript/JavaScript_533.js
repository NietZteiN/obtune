function f(query, base){
    let net_sum = 0;
    for (let key in base) {
        let val = base[key];
        if (key[0] === query && key.length === 3) {
            net_sum -= val;
        } else if (key[key.length - 1] === query && key.length === 3) {
            net_sum += val;
        }
    }
    return net_sum;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("a", {}),0);
}

test();
