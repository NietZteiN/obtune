package f_test

import (
    "testing"
    "fmt"
)

func f(lst []int) []int {
    for i := 0; i < len(lst); i++ {
        for j := i + 1; j < len(lst); j++ {
            if lst[j] < lst[i] {
                lst[i], lst[j] = lst[j], lst[i]
            }
        }
    }
    return lst[:3]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{5, 8, 1, 3, 0}), expected: []int{0, 1, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
