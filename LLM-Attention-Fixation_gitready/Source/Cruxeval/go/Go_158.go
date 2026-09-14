package f_test

import (
	"testing"
	"fmt"
)

func f(arr []int) []int {
	var n []int
	for _, item := range arr {
		if item%2 == 0 {
			n = append(n, item)
		}
	}
	m := append(n, arr...)
	for i := 0; i < len(m); i++ {
		if m[i]%2 != 0 {
			m = append(m[:i], m[i+1:]...)
			i-- // after removing i, the next item will be in this index
		}
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
     { actual: candidate([]int{3, 6, 4, -2, 5}), expected: []int{6, 4, -2, 6, 4, -2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
