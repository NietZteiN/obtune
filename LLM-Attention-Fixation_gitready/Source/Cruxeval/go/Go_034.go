package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, odd1 int, odd2 int) []int {
    for i := 0; i < len(nums); {
        if nums[i] == odd1 {
            nums = append(nums[:i], nums[i+1:]...)
        } else if nums[i] == odd2 {
            nums = append(nums[:i], nums[i+1:]...)
        } else {
            i++
        }
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
     { actual: candidate([]int{1, 2, 3, 7, 7, 6, 8, 4, 1, 2, 3, 5, 1, 3, 21, 1, 3}, 3, 1), expected: []int{2, 7, 7, 6, 8, 4, 2, 5, 21} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
