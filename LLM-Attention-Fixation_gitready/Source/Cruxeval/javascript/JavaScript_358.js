function f(text, value){
    let indexes = [];
    for(let i = 0; i < text.length; i++) {
        if (text[i] === value && (i === 0 || text[i-1] !== value)) {
            indexes.push(i);
        }
    }
    if (indexes.length % 2 === 1) {
        return text;
    }
    return text.slice(indexes[0] + 1, indexes[indexes.length - 1]);
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("btrburger", "b"),"tr");
}

test();
