function f(years){
    const a10 = years.filter(x => x <= 1900).length;
    const a90 = years.filter(x => x > 1910).length;
    if (a10 > 3) {
        return 3;
    } else if (a90 > 3) {
        return 1;
    } else {
        return 2;
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1872, 1995, 1945]),2);
}

test();
