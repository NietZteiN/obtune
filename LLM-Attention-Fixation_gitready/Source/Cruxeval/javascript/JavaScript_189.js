function f(out, mapping){
    for (let key in mapping) {
        out = out.replace(new RegExp(`{${key}}`, 'g'), mapping[key][1]);
        if (!out.match(/{\w}/)) {
            break;
        }
    }
    return out;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("{{{{}}}}", {}),"{{{{}}}}");
}

test();
