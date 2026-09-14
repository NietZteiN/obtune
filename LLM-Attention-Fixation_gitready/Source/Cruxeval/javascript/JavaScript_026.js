function f(items, target){
    let itemsArr = items.split(' ');
    for (let i = 0; i < itemsArr.length; i++) {
        if (target.includes(itemsArr[i])) {
            return items.indexOf(itemsArr[i]) + 1;
        }
        if (itemsArr[i].indexOf('.') === itemsArr[i].length - 1 || itemsArr[i].indexOf('.') === 0) {
            return 'error';
        }
    }
    return '.';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("qy. dg. rnvprt rse.. irtwv tx..", "wtwdoacb"),"error");
}

test();
