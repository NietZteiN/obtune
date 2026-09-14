function f(countries){
    let language_country = {};
    for (let country in countries) {
        let language = countries[country];
        if (!language_country[language]) {
            language_country[language] = [];
        }
        language_country[language].push(country);
    }
    return language_country;
}
const assert = require('node:assert');


function test() {
  let candidate = f;
  assert.deepEqual(candidate({}),{});
}

test();
