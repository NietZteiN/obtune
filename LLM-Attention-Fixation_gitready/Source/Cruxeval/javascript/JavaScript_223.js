function f(array, target){
    let count = 0;
    let i = 1;
    for (let j = 1; j < array.length; j++) {
        if (array[j] > array[j-1] && array[j] <= target) {
            count += i;
        } else if (array[j] <= array[j-1]) {
            i = 1;
        } else {
            i += 1;
        }
    }
    return count;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([1, 2, -1, 4], 2),1);
}

test();
