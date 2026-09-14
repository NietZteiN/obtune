function f(text, chars){
    if(chars){
        text = text.replace(new RegExp('[' + chars + ']+$'), '');
    } else {
        text = text.trimRight();
    }
    if (text === ''){
        return '-';
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("new-medium-performing-application - XQuery 2.2", "0123456789-"),"new-medium-performing-application - XQuery 2.");
}

test();
