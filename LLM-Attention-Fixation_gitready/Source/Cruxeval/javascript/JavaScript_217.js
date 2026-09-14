function f(string){
    if (string.match(/^[a-zA-Z0-9]+$/)) {
        return "ascii encoded is allowed for this language";
    }
    return "more than ASCII";
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("Str zahrnuje anglo-ameriæske vasi piscina and kuca!"),"more than ASCII");
}

test();
