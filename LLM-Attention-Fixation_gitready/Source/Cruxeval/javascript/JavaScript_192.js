function f(text, suffix){
    let output = text;
    while (text.endsWith(suffix)) {
        output = text.slice(0, -suffix.length);
        text = output;
    }
    return output;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("!klcd!ma:ri", "!"),"!klcd!ma:ri");
}

test();
