function f(data){
    let members = [];
    for (let item in data) {
        for (let member of data[item]) {
            if (!members.includes(member)) {
                members.push(member);
            }
        }
    }
    return members.sort();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"inf": ["a", "b"], "a": ["inf", "c"], "d": ["inf"]}),["a", "b", "c", "inf"]);
}

test();
