package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, delete int) []int {
    for i, num := range nums {
        if num == delete {
            nums = append(nums[:i], nums[i+1:]...)
            break
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
     { actual: candidate([]int{4, 5, 3, 6, 1}, 5), expected: []int{4, 3, 6, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
