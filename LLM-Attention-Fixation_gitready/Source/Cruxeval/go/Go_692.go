package f_test

import (
    "testing"
    "fmt"
)

func f(array []int) []int {
    a := []int{}
    for i := len(array) - 1; i >= 0; i-- {
        if array[i] != 0 {
            a = append(a, array[i])
        }
    }
    return a
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
