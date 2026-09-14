package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    count := 1
    for i := count; i < len(nums)-1; i += 2 {
        if nums[i] < nums[count-1] {
            nums[i] = nums[count-1]
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
     { actual: candidate([]int{1, 2, 3}), expected: []int{1, 2, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
