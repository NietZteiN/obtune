package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, n int) int {
    value := nums[n]
    nums = append(nums[:n], nums[n+1:]...)
    return value
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{-7, 3, 1, -1, -1, 0, 4}, 6), expected: 4 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
