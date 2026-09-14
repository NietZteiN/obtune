package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, start int, k int) []int {
    reversed := make([]int, k)
    for i := 0; i < k; i++ {
        reversed[i] = nums[start+k-1-i]
    }
    copy(nums[start:start+k], reversed)
    return nums
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 3, 4, 5, 6}, 4, 2), expected: []int{1, 2, 3, 4, 6, 5} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
