package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int, target int) int {
    cnt := 0
    for _, num := range nums {
        if num == target {
            cnt++
        }
    }
    return cnt * 2
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 1}, 1), expected: 4 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
