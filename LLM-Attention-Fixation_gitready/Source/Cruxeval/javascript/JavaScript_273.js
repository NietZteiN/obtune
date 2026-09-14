function f(name){
    let new_name = '';
    name = name.split('').reverse().join('');
    for(let i = 0; i < name.length; i++){
        let n = name[i];
        if(n !== '.' && new_name.split('.').length < 3){
            new_name = n + new_name;
        }else{
            break;
        }
    }
    return new_name;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(".NET"),"NET");
}

test();
