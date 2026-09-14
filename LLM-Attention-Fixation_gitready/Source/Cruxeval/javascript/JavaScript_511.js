function f(fields, update_dict){
    let di = {};
    fields.forEach(x => di[x] = '');
    Object.assign(di, update_dict);
    return di;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["ct", "c", "ca"], {"ca": "cx"}),{"ct": "", "c": "", "ca": "cx"});
}

test();
