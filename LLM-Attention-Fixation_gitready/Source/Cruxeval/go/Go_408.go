package f_test

import (
    "testing"
    "fmt"
)

func f(m []int) []int {
    for i, j := 0, len(m)-1; i < j; i, j = i+1, j-1 {
        m[i], m[j] = m[j], m[i]
    }
    return m
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{-4, 6, 0, 4, -7, 2, -1}), expected: []int{-1, 2, -7, 4, 0, 6, -4} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
