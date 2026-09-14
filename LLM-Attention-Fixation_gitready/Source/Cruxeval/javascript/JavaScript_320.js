function f(text){
    let index = 1;
    while (index < text.length) {
        if (text[index] !== text[index - 1]) {
            index++;
        } else {
            let text1 = text.slice(0, index);
            let text2 = text.slice(index).split('').map(char => char === char.toUpperCase() ? char.toLowerCase() : char.toUpperCase()).join('');
            return text1 + text2;
        }
    }
    return text.split('').map(char => char === char.toUpperCase() ? char.toLowerCase() : char.toUpperCase()).join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("USaR"),"usAr");
}

test();
