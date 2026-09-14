function f(text){
    let words = text.split(' ');
    for (let i = 0; i < words.length; i++) {
        text = text.replace(`-${words[i]}`, ' ').replace(`${words[i]}-`, ' ');
    }
    return text.replace(/^-+|[- ]+$/g, '');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("-stew---corn-and-beans-in soup-.-"),"stew---corn-and-beans-in soup-.");
}

test();
