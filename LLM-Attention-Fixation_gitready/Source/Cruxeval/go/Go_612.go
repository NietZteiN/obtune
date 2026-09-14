package f_test

import (
    "testing"
    "fmt"
)

func f(d map[string]int) map[string]int {
    return d
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"a": 42, "b": 1337, "c": -1, "d": 5}), expected: map[string]int{"a": 42, "b": 1337, "c": -1, "d": 5} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
