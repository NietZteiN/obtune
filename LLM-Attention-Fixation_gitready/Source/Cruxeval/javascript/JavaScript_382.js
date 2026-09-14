function f(a){
    let s = {};
    const items = Object.entries(a);
    items.reverse().forEach((item) => {
        s[item[0]] = item[1];
    });
    let str = '';
    for (let key in s) {
        str += `(${key}, '${s[key]}') `;
    }
    return str.trim();
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({15: "Qltuf", 12: "Rwrepny"}),"(12, 'Rwrepny') (15, 'Qltuf')");
}

test();
