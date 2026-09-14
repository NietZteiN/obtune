function f(text, speaker){
    while(text.startsWith(speaker)){
        text = text.slice(speaker.length);
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("[CHARRUNNERS]Do you know who the other was? [NEGMENDS]", "[CHARRUNNERS]"),"Do you know who the other was? [NEGMENDS]");
}

test();
