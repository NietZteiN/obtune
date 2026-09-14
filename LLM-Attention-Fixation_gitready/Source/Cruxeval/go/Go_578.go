package f_test

import (
    "testing"
    "fmt"
)

func f(obj map[string]int) map[string]int {
    for k, v := range obj {
        if v >= 0 {
            obj[k] = -v
        }
    }
    return obj
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"R": 0, "T": 3, "F": -6, "K": 0}), expected: map[string]int{"R": 0, "T": -3, "F": -6, "K": 0} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
