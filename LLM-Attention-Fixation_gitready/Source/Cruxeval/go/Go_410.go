package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    a := 0
    for i := range nums {
        nums = append(nums[:i], append([]int{nums[a]}, nums[i:]...)...)
        a += 1
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
     { actual: candidate([]int{1, 3, -1, 1, -2, 6}), expected: []int{1, 1, 1, 1, 1, 1, 1, 3, -1, 1, -2, 6} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
