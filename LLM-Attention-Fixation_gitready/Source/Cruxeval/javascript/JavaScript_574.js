function f(simpons){
    while(simpons.length > 0){
        let pop = simpons.pop();
        if(pop === pop.charAt(0).toUpperCase() + pop.slice(1)){
            return pop;
        }
    }
    return pop;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate(["George", "Michael", "George", "Costanza"]),"Costanza");
}

test();
