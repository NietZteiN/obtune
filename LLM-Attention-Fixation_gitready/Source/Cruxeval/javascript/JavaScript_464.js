function f(ans){
    if(!isNaN(ans) && parseInt(ans) >= 0 && parseInt(ans) % 1 === 0){
        let total = parseInt(ans) * 4 - 50;
        let count = 0;
        const charList = ans.split('');
        for(let i = 0; i < charList.length; i++){
            if(!['0', '2', '4', '6', '8'].includes(charList[i])){
                count += 1;
            }
        }
        total -= count * 100;
        return total;
    }
    return 'NAN';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("0"),-50);
}

test();
