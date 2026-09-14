package f_test

import (
    "testing"
    "fmt"
)

func f(plot []int, delin int) []int {
    for i, val := range plot {
        if val == delin {
            first := plot[:i]
            second := plot[i+1:]
            return append(first, second...)
        }
    }
    return plot
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 3, 4}, 3), expected: []int{1, 2, 4} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
