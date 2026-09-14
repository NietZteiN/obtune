package f_test

import (
    "fmt"
    "testing"
)

func f(nums []int) []int {
    count := make([]int, len(nums))
    for range nums {
        nums = nums[:len(nums)-1]
        if len(count) > 0 {
            count = count[1:]
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
     { actual: candidate([]int{3, 1, 7, 5, 6}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
