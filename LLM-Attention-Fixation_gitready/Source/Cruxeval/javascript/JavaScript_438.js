function f(string){
    let bigTab = 100;
    for (let i = 10; i < 30; i++){
        if (string.split('\t').length > 1 && string.split('\t').length < 20){
            bigTab = i;
            break;
        }
    }
    return expandTabs(string, bigTab);
}

function expandTabs(str, bigTab){
    let newStr = '';
    let count = 0;
    for (let i = 0; i < str.length; i++){
        if (str[i] == '\t'){
            let spaces = bigTab - (count % bigTab);
            newStr += ' '.repeat(spaces);
            count += spaces;
        } else {
            newStr += str[i];
            count++;
        }
    }
    return newStr;
}

const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(`1  			3`),"1                             3");
}

test();
