function f(x){
    if (x.length === 0) {
        return -1;
    } else {
        let cache = {};
        x.forEach(item => {
            if (cache[item]) {
                cache[item] += 1;
            } else {
                cache[item] = 1;
            }
        });
        return Math.max(...Object.values(cache));
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 0, 2, 2, 0, 0, 0, 1]),4);
}

test();
