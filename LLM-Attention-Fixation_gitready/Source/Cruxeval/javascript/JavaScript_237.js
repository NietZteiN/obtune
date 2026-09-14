function f(text, char){
    if (text.includes(char)) {
        let [suff, pref] = text.split(char);
        pref = suff.slice(0, -char.length) + suff.slice(char.length) + char + pref;
        return suff + char + pref;
    }
    return text;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("uzlwaqiaj", "u"),"uuzlwaqiaj");
}

test();
