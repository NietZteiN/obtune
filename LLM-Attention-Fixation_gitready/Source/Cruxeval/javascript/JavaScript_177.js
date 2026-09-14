function f(text){
    text = text.split('');
    for (let i = 0; i < text.length; i++) {
        if (i % 2 === 1) {
            text[i] = text[i].toUpperCase() === text[i] ? text[i].toLowerCase() : text[i].toUpperCase();
        }
    }
    return text.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Hey DUdE THis $nd^ &*&this@#"),"HEy Dude tHIs $Nd^ &*&tHiS@#");
}

test();
