package f_test

import (
	"testing"
	"fmt"
)

func f(aDict map[int]int) map[int]int {
    // transpose the keys and values into a new dict
    newDict := make(map[int]int)
    for k, v := range aDict {
        newDict[v] = k
    }
    return newDict
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{1: 1, 2: 2, 3: 3}), expected: map[int]int{1: 1, 2: 2, 3: 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
