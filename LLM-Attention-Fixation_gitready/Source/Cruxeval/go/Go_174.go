package f_test

import (
    "testing"
    "fmt"
)

func f(lst []int) []int {
    for i, j := 1, 3; i < j; i, j = i+1, j-1 {
        lst[i], lst[j-1] = lst[j-1], lst[i]
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
     { actual: candidate([]int{1, 2, 3}), expected: []int{1, 3, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
