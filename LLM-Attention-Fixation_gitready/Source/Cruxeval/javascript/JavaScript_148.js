function f(forest, animal){
    let index = forest.indexOf(animal);
    let result = forest.split('');
    while (index < forest.length - 1) {
        result[index] = forest[index + 1];
        index++;
    }
    if (index === forest.length - 1) {
        result[index] = '-';
    }
    return result.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("2imo 12 tfiqr.", "m"),"2io 12 tfiqr.-");
}

test();
