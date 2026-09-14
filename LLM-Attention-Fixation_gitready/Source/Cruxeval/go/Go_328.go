package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, L int) []int {
    if L <= 0 {
        return array
    }
    if len(array) < L {
        array = append(array, f(array, L - len(array))...)
    }
    return array
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 3}, 4), expected: []int{1, 2, 3, 1, 2, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
