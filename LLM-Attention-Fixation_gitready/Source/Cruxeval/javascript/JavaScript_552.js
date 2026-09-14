function f(d){
    let result = {};
    for (let [k, v] of Object.entries(d)) {
        if (typeof k === 'number' && Number.isFinite(k)) {
            if (Array.isArray(v)) {
                v.forEach(i => {
                    result[i] = k;
                });
            }
        } else {
            result[k] = v;
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({2: 0.76, 5: [3, 6, 9, 12]}),{2: 0.76, 5: [3, 6, 9, 12]});
}

test();
