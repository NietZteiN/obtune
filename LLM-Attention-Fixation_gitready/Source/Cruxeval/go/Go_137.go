package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    count := 0
    for len(nums) > 0 {
        if count%2 == 0 {
            nums = nums[:len(nums)-1]
        } else {
            nums = nums[1:]
        }
        count++
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
     { actual: candidate([]int{3, 2, 0, 0, 2, 3}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
