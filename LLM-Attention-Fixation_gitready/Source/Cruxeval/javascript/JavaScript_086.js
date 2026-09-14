function f(instagram, imgur, wins){
    let photos = [instagram, imgur];
    if (instagram.toString() === imgur.toString()) {
        return wins;
    }
    if (wins === 1) {
        return photos.pop();
    } else {
        photos.reverse();
        return photos.pop();
    }
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["sdfs", "drcr", "2e"], ["sdfs", "dr2c", "QWERTY"], 0),["sdfs", "drcr", "2e"]);
}

test();
