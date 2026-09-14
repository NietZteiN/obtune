package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, pop1 int, pop2 int) []int {
    // Go slice is not a dynamic array, so we need to manually remove elements and re-slice
    // First, remove the element at index pop1 - 1
    nums = append(nums[:pop1-1], nums[pop1:]...)
    // Second, remove the element at index pop2 - 1 (note that after the first pop, the array has become one element shorter)
    nums = append(nums[:pop2-1], nums[pop2:]...)
    return nums
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 5, 2, 3, 6}, 2, 4), expected: []int{1, 2, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
