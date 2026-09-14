package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    count := len(nums)
    for i := 0; i < count/2; i++ {
        nums[i], nums[count-i-1] = nums[count-i-1], nums[i]
    }
    return nums
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{2, 6, 1, 3, 1}), expected: []int{1, 3, 1, 6, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
