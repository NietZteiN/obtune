function f(messages){
    let phone_code = "+353";
    let result = [];
    for (let message of messages) {
        message.push(...phone_code);
        result.push(message.join(";"));
    }
    return result.join(". ");
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate([["Marie", "Nelson", "Oscar"]]),"Marie;Nelson;Oscar;+;3;5;3");
}

test();
