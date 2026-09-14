function f(st) {
    let lower_st = st.toLowerCase();
    let last_h_index = lower_st.lastIndexOf('h');
    let last_i_index = lower_st.lastIndexOf('i');
    if (last_h_index >= last_i_index) {
        return 'Hey';
    } else {
        return 'Hi';
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Hi there"),"Hey");
}

test();
