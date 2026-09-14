package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, spot int, idx int) []int {
    result := make([]int, len(nums)+1)
    copy(result, nums[:spot])
    result[spot] = idx
    copy(result[spot+1:], nums[spot:])
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 0, 1, 1}, 0, 9), expected: []int{9, 1, 0, 1, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
