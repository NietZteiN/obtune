function f(dic){
    let sortedItems = Object.entries(dic).sort((a, b) => String(a).length - String(b).length).slice(0, -1);
    sortedItems.forEach(([key]) => delete dic[key]);
    return Object.entries(dic);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"11": 52, "65": 34, "a": 12, "4": 52, "74": 31}),[["74", 31]]);
}

test();
