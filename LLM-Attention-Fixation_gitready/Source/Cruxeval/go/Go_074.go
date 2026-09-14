package f_test

import (
    "testing"
    "fmt"
)

func f(lst []int, i int, n int) []int {
    lst = append(lst[:i], append([]int{n}, lst[i:]...)...)
    return lst
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{44, 34, 23, 82, 24, 11, 63, 99}, 4, 15), expected: []int{44, 34, 23, 82, 15, 24, 11, 63, 99} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
