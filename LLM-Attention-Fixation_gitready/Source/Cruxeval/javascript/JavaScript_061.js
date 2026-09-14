function f(text){
    let texts = text.split(' ');
    if (texts.length > 0) {
        let xtexts = texts.filter(t => t.match(/^[\x00-\x7F]+$/) && !['nada', '0'].includes(t));
        return xtexts.reduce((a, b) => a.length >= b.length ? a : b, 'nada');
    }
    return 'nada';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(""),"nada");
}

test();
