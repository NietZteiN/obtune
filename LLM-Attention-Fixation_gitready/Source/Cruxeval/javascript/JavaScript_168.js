function f(text, new_value, index){
    let key = text.substring(index, index + 1);
    let keyValue = key.charCodeAt(0);
    let newValue = new_value.charCodeAt(0);
    let keyMap = {};
    keyMap[keyValue] = newValue;
    let result = "";
    
    for (let i = 0; i < text.length; i++) {
        if (text.charCodeAt(i) in keyMap) {
            result += String.fromCharCode(keyMap[text.charCodeAt(i)]);
        } else {
            result += text.charAt(i);
        }
    }
    return result;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("spain", "b", 4),"spaib");
}

test();
