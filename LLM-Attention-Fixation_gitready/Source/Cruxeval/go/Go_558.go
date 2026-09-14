package f_test

import (
    "fmt"
    "testing"
    "sort"
)

func f(nums []int, mos []int) bool {
    for _, num := range mos {
        index := -1
        for i, n := range nums {
            if n == num {
                index = i
                break
            }
        }
        nums = append(nums[:index], nums[index+1:]...)
    }
    sort.Ints(nums)
    nums = append(nums, mos...)
    for i := 0; i < len(nums)-1; i++ {
        if nums[i] > nums[i+1] {
            return false
        }
    }
    return true
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{3, 1, 2, 1, 4, 1}, []int{1}), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
