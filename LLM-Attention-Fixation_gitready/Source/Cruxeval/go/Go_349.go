package f_test

import (
    "testing"
    "fmt"
)

func f(dictionary map[string]int) map[string]int {
    dictionary["1049"] = 55
    for key, value := range dictionary {
        delete(dictionary, key)
        dictionary[key] = value
        break
    }
    return dictionary
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"noeohqhk": 623}), expected: map[string]int{"noeohqhk": 623, "1049": 55} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
