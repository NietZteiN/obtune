package f_test

import (
    "fmt"
    "testing"
)

func f(base_list []int, nums []int) []int {
    base_list = append(base_list, nums...)
    res := make([]int, len(base_list))
    copy(res, base_list)
    for i := len(nums); i > 0; i-- {
        res = append(res, res[len(res)-i])
    }
    return res
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{9, 7, 5, 3, 1}, []int{2, 4, 6, 8, 0}), expected: []int{9, 7, 5, 3, 1, 2, 4, 6, 8, 0, 2, 6, 0, 6, 6} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
