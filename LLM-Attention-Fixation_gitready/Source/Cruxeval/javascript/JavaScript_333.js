function f(places, lazy){
    places.sort();
    for (let l of lazy) {
        places.splice(places.indexOf(l), 1);
    }
    if (places.length === 1) {
        return 1;
    }
    for (let i = 0; i < places.length; i++) {
        if (places.filter(place => places.includes(place + 1)).length === 0) {
            return i + 1;
        }
    }
    return i + 1;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([375, 564, 857, 90, 728, 92], [728]),1);
}

test();
