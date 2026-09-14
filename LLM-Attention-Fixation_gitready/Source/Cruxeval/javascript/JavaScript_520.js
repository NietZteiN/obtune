function f(album_sales){
    while(album_sales.length !== 1){
        album_sales.push(album_sales.shift());
    }
    return album_sales[0];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([6]),6);
}

test();
