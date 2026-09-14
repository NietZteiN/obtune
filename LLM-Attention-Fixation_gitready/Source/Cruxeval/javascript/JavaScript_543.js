function f(item){
    let modified = item.replace('. ', ' , ').replace('&#33; ', '! ').replace('. ', '? ').replace('. ', '. ');
    return modified.charAt(0).toUpperCase() + modified.slice(1);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(".,,,,,. منبت"),".,,,,, , منبت");
}

test();
