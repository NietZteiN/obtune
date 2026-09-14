function f(marks){
    let highest = 0;
    let lowest = 100;
    for (let value of Object.values(marks)) {
        if (value > highest) {
            highest = value;
        }
        if (value < lowest) {
            lowest = value;
        }
    }
    return [highest, lowest];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"x": 67, "v": 89, "": 4, "alij": 11, "kgfsd": 72, "yafby": 83}),[89, 4]);
}

test();
