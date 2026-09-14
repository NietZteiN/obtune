package f_test

import (
    "testing"
    "fmt"
)

func f(lst []int) []int {
    for i := len(lst) - 1; i > 0; i-- {
        for j := 0; j < i; j++ {
            if lst[j] > lst[j+1] {
                lst[j], lst[j+1] = lst[j+1], lst[j]
            }
        }
    }
    return lst
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{63, 0, 1, 5, 9, 87, 0, 7, 25, 4}), expected: []int{0, 0, 1, 4, 5, 7, 9, 25, 63, 87} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
