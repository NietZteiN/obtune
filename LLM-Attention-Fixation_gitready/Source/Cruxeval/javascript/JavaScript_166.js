function f(graph){
    let new_graph = {};
    for (let key in graph) {
        new_graph[key] = {};
        for (let subkey in graph[key]) {
            new_graph[key][subkey] = '';
        }
    }
    return new_graph;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}),{});
}

test();
