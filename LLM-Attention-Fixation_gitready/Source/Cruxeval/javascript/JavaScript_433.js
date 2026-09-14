function f(text){
    text = text.split(',');
    text.shift();
    text.unshift(text.splice(text.indexOf('T'), 1)[0]);
    return 'T,' + text.join(',');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Dmreh,Sspp,T,G ,.tB,Vxk,Cct"),"T,T,Sspp,G ,.tB,Vxk,Cct");
}

test();
