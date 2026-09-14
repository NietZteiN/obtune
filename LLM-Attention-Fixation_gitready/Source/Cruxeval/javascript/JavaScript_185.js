function f(L){
    const N = L.length;
    for (let k = 1; k <= Math.floor(N / 2); k++) {
        let i = k - 1;
        let j = N - k;
        while (i < j) {
            // swap elements:
            [L[i], L[j]] = [L[j], L[i]];
            // update i, j:
            i++;
            j--;
        }
    }
    return L;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([16, 14, 12, 7, 9, 11]),[11, 14, 7, 12, 9, 16]);
}

test();
