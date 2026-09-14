package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) int {
    counts := 0
    for _, i := range nums {
        if fmt.Sprintf("%d", i) == fmt.Sprintf("%v", i) {
            if counts == 0 {
                counts++
            }
        }
    }
    return counts
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{0, 6, 2, -1, -2}), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
