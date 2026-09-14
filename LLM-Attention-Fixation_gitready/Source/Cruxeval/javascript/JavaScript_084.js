function f(text){
    let arr = text.split(' ');
    let result = [];
    for(let item of arr){
        if(item.endsWith('day')){
            item += 'y';
        } else {
            item += 'day';
        }
        result.push(item);
    }
    return result.join(' ');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("nwv mef ofme bdryl"),"nwvday mefday ofmeday bdrylday");
}

test();
