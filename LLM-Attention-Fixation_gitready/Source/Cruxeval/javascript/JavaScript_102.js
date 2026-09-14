function f(names, winners){
    let ls = names.reduce((acc, name, index) => {
        if (winners.includes(name)) {
            acc.push(index);
        }
        return acc;
    }, []);
    ls.sort((a, b) => b - a);
    return ls;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["e", "f", "j", "x", "r", "k"], ["a", "v", "2", "im", "nb", "vj", "z"]),[]);
}

test();
