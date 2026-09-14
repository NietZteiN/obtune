function f(names){
    let parts = names.split(',');
    for(let i=0; i<parts.length; i++){
        parts[i] = parts[i].replace(' and', '+').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ').replace('+', ' and');
    }
    return parts.join(', ');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("carrot, banana, and strawberry"),"Carrot,  Banana,  and Strawberry");
}

test();
