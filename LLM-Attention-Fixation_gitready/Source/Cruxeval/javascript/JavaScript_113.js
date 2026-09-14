function f(line){
    let count = 0;
    let a = [];
    for(let i=0; i<line.length; i++){
        count += 1;
        if(count%2===0){
            a.push(line[i].toLowerCase() === line[i] ? line[i].toUpperCase() : line[i].toLowerCase());
        }else{
            a.push(line[i]);
        }
    }
    return a.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("987yhNSHAshd 93275yrgSgbgSshfbsfB"),"987YhnShAShD 93275yRgsgBgssHfBsFB");
}

test();
