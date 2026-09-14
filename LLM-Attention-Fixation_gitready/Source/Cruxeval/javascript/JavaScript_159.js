function f(st){
    let swapped = '';
    for(let i = st.length - 1; i >= 0; i--){
        swapped += st[i].toUpperCase() === st[i] ? st[i].toLowerCase() : st[i].toUpperCase();
    }
    return swapped;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("RTiGM"),"mgItr");
}

test();
