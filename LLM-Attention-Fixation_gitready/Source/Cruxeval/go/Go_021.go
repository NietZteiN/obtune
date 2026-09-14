package f_test

import (
    "testing"
    "fmt"
)

func f(array []int) []int {
    n := array[len(array)-1]
    array = array[:len(array)-1]
    array = append(array, n, n)
    return array
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 1, 2, 2}), expected: []int{1, 1, 2, 2, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
