function f(text){
    text = text.replace(' x', ' x.');
    if (text[0].toUpperCase() === text[0]) {
        return 'correct';
    }
    text = text.replace(' x.', ' x');
    return 'mixed';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("398 Is A Poor Year To Sow"),"correct");
}

test();
