package f_test

import (
    "testing"
    "fmt"
)

func f(arr []int) []int {
    count := len(arr)
    sub := make([]int, count)
    copy(sub, arr)
    for i := 0; i < count; i += 2 {
        sub[i] *= 5
    }
    return sub
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{-3, -6, 2, 7}), expected: []int{-15, -6, 10, 7} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
