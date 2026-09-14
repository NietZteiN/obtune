function f(sentence){
    let ls = sentence.split('');
    for(let letter of ls){
        if(letter === letter.toLowerCase()){
            ls.splice(ls.indexOf(letter), 1);
        }
    }
    return ls.join('');
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate("XYZ LittleRedRidingHood LiTTleBIGGeXEiT fault"),"XYZLtRRdnHodLTTBIGGeXET fult");
}

test();
