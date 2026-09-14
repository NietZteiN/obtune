function f(student_marks, name){
    if (student_marks.hasOwnProperty(name)) {
        var value = student_marks[name];
        delete student_marks[name];
        return value;
    }
    return 'Name unknown';
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({"882afmfp": 56}, "6f53p"),"Name unknown");
}

test();
