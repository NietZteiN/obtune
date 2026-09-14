package f_test

import (
    "testing"
    "fmt"
)

func f(lst []int) []int {
    for i, j := 0, len(lst)-1; i < j; i, j = i+1, j-1 {
        lst[i], lst[j] = lst[j], lst[i]
    }
    lst = lst[:len(lst)-1]
    for i, j := 0, len(lst)-1; i < j; i, j = i+1, j-1 {
        lst[i], lst[j] = lst[j], lst[i]
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
     { actual: candidate([]int{7, 8, 2, 8}), expected: []int{8, 2, 8} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
