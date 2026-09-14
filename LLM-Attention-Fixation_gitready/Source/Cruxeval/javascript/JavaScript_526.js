function f(label1, char, label2, index){
    var m = label1.lastIndexOf(char);
    if (m >= index) {
        return label2.substring(0, m - index + 1);
    }
    return label1 + label2.substring(index - m - 1);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("ekwies", "s", "rpg", 1),"rpg");
}

test();
