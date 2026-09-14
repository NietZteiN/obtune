function lstrip(text, chars) {
    let start = 0;
    while (start < text.length && chars.includes(text[start])) {
        start++;
    }
    return text.substring(start);
}

function rstrip(text, chars) {
    let end = text.length - 1;
    while (end >= 0 && chars.includes(text[end])) {
        end--;
    }
    return text.substring(0, end + 1);
}

function f(text, froms) {
    text = lstrip(text, froms);
    text = rstrip(text, froms);
    return text;
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("0 t 1cos ", `st 0	
  `),"1co");
}

test();
