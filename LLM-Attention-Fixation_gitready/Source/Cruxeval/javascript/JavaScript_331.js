function f(strand, zmnc){
    let poz = strand.indexOf(zmnc);
    while (poz !== -1) {
        strand = strand.substring(poz + 1);
        poz = strand.indexOf(zmnc);
    }
    return strand.lastIndexOf(zmnc);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("", "abc"),-1);
}

test();
