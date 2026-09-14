function f(text, width){
    let result = text.substring(0, width);
    while(result.length < width){
        result = 'z' + result + 'z';
        if(result.length > width) {
            result = result.substring(0, width);
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("0574", 9),"zzz0574zz");
}

test();
