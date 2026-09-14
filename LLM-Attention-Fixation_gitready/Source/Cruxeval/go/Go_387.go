package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, pos int, value int) []int {
    nums = append(nums[:pos], append([]int{value}, nums[pos:]...)...)
    return nums
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{3, 1, 2}, 2, 0), expected: []int{3, 1, 0, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
