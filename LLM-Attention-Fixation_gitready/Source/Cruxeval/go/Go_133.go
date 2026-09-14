package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, elements []int) []int {
    result := []int{}
    for _ = range elements {
        popped := nums[len(nums)-1]
        nums = nums[:len(nums)-1]
        result = append(result, popped)
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
     { actual: candidate([]int{7, 1, 2, 6, 0, 2}, []int{9, 0, 3}), expected: []int{7, 1, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
