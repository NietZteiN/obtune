function f(text){
    let splittedText = text.split('|');
    let problem = splittedText.pop();
    let topic = splittedText.length > 0 ? splittedText.join('|') : '';

    if (problem === 'r') {
        problem = topic.replace(/u/g, 'p');
    }

    return [topic, problem];
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("|xduaisf"),["", "xduaisf"]);
}

test();
