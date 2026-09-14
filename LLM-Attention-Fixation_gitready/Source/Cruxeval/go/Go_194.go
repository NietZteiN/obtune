package f_test

import (
	"testing"
	"fmt"
)

func f(matr [][]int, insert_loc int) [][]int {
	// Append a new slice to the end of the matrix
	matr = append(matr, []int{})

	// Move the elements to the right from the insertion location
	copy(matr[insert_loc+1:], matr[insert_loc:])

	// Insert an empty slice at the insertion location
	matr[insert_loc] = []int{}

	return matr
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([][]int{[]int{5, 6, 2, 3}, []int{1, 9, 5, 6}}, 0), expected: []interface{}{[]interface{}{}, []int{5, 6, 2, 3}, []int{1, 9, 5, 6}} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
