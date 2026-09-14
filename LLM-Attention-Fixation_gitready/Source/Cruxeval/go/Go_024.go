package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, i int) []int {
    return append(nums[:i], nums[i+1:]...)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{35, 45, 3, 61, 39, 27, 47}, 0), expected: []int{45, 3, 61, 39, 27, 47} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
