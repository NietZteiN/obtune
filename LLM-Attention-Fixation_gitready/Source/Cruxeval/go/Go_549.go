package f_test

import (
    "testing"
    "fmt"
)

func f(matrix [][]int) [][]int {
    for i := 0; i < len(matrix); i++ {
        for j := 0; j < len(matrix[i]); j++ {
            max := matrix[i][0]
            for k := 1; k < len(matrix[i]); k++ {
                if matrix[i][k] > max {
                    max = matrix[i][k]
                }
            }
            for k := 0; k < len(matrix[i]); k++ {
                if matrix[i][k] < max {
                    matrix[i][k] = 0
                }
            }
            for l := 0; l < len(matrix[i])-1; l++ {
                for m := 0; m < len(matrix[i])-1-l; m++ {
                    if matrix[i][m] < matrix[i][m+1] {
                        matrix[i][m], matrix[i][m+1] = matrix[i][m+1], matrix[i][m]
                    }
                }
            }
        }
    }
    return matrix
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([][]int{[]int{1, 1, 1, 1}}), expected: [][]int{[]int{1, 1, 1, 1}} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
