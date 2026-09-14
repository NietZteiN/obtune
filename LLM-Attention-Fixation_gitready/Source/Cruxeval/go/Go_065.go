package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, index int) int {
    val := nums[index] % 42 + nums[index]*2
    nums = append(nums[:index], nums[index+1:]...)
    return val
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{3, 2, 0, 3, 7}, 3), expected: 9 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
