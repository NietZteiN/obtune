package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    m := 0
    for _, num := range nums {
        if num > m {
            m = num
        }
    }

    for i := 0; i < m; i++ {
        for left, right := 0, len(nums)-1; left < right; left, right = left+1, right-1 {
            nums[left], nums[right] = nums[right], nums[left]
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
     { actual: candidate([]int{43, 0, 4, 77, 5, 2, 0, 9, 77}), expected: []int{77, 9, 0, 2, 5, 77, 4, 0, 43} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
