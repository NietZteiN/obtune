function f(vectors){
    let sorted_vecs = [];
    vectors.forEach(vec => {
        vec.sort();
        sorted_vecs.push(vec);
    });
    return sorted_vecs;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([]),[]);
}

test();
