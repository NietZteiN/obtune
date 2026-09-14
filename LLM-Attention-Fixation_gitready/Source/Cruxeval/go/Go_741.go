package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, p int) int {
    prev_p := p - 1
    if prev_p < 0 {
        prev_p = len(nums) - 1
    }
    return nums[prev_p]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{6, 8, 2, 5, 3, 1, 9, 7}, 6), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
