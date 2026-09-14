function f(text){
    let dic = {};
    for(let i = 0; i < text.length; i++){
        if(dic[text[i]]){
            dic[text[i]]++;
        } else {
            dic[text[i]] = 1;
        }
    }
    for(let key in dic){
        if(dic[key] > 1){
            dic[key] = 1;
        }
    }
    return dic;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("a"),{"a": 1});
}

test();
