function f(dic, inx){
    try {
        let keys = Object.keys(dic);
        let index = keys.indexOf(inx);
        if (index !== -1) {
            dic[keys[index]] = keys[index].toLowerCase();
        }
    } catch (error) {
        // pass
    }
    return Object.entries(dic);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"Bulls": 23, "White Sox": 45}, "Bulls"),[["Bulls", "bulls"], ["White Sox", 45]]);
}

test();
