function f(text){
    for(let p of ['acs', 'asp', 'scn']){
        text = text.replace(new RegExp(`^${p}`), '') + ' ';
    }
    return text.replace(new RegExp('^ '), '').slice(0, -1);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ilfdoirwirmtoibsac"),"ilfdoirwirmtoibsac  ");
}

test();
