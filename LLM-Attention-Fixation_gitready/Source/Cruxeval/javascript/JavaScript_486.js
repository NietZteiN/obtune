function f(dic){
    let dic_op = Object.assign({}, dic);
    for (let key in dic) {
        dic_op[key] = dic[key] * dic[key];
    }
    return dic_op;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({1: 1, 2: 2, 3: 3}),{1: 1, 2: 4, 3: 9});
}

test();
