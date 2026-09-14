function f(s, p){
    let arr = s.split(p);
    if (arr.length > 1) {
        let part_one = arr[0].length;
        let part_two = arr[1].length;
        let part_three = arr.slice(2).join('').length;
        if (part_one >= 2 && part_two <= 2 && part_three >= 2){
            return arr[0].split('').reverse().join('') + arr[1] + arr[2].split('').reverse().join('') + '#';
        }
    }
    return s;
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("qqqqq", "qqq"),"qqqqq");
}

test();
