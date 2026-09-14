function f(tuple_list, joint){
    let string = '';
    for(let num of tuple_list){
        string += Array.from(new Set(String(num))).pop() + joint;
    }
    return string;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([32332, 23543, 132323, 33300], ","),"2,4,2,0,");
}

test();
