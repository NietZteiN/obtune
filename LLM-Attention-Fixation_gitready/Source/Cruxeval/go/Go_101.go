package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, i_num int, elem int) []int {
    array = append(array[:i_num], append([]int{elem}, array[i_num:]...)...)
    return array
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{-4, 1, 0}, 1, 4), expected: []int{-4, 4, 1, 0} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
