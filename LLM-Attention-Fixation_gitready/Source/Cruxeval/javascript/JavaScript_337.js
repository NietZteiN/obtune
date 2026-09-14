function f(txt){
    let d = [];
    for(let i = 0; i < txt.length; i++){
        let c = txt[i];
        if (!isNaN(parseInt(c, 10))) {
            continue;
        }
        if (c === c.toLowerCase()) {
            d.push(c.toUpperCase());
        } else if (c === c.toUpperCase()) {
            d.push(c.toLowerCase());
        }
    }
    return d.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("5ll6"),"LL");
}

test();
