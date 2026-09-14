package f_test

import (
    "testing"
    "fmt"
)

func f(lst []int) []int {
    new := make([]int, 0)
    i := len(lst) - 1
    for range lst {
        if i%2 == 0 {
            new = append(new, -lst[i])
        } else {
            new = append(new, lst[i])
        }
        i--
    }
    return new
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 7, -1, -3}), expected: []int{-3, 1, 7, -1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
