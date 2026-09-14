package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    // Pass in a copy to avoid modifying nums
    numsCopy := make([]int, len(nums))
    copy(numsCopy, nums)

    count := len(numsCopy)
    for i := -count + 1; i < 0; i++ {
        numsCopy = append([]int{numsCopy[len(numsCopy)+i]}, numsCopy...)
    }

    return numsCopy
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{7, 1, 2, 6, 0, 2}), expected: []int{2, 0, 6, 2, 1, 7, 1, 2, 6, 0, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
