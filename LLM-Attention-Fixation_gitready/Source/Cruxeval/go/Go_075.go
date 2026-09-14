package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, elem int) int {
    ind := 0
    for i, val := range array {
        if val == elem {
            ind = i
            break
        }
    }
    return ind*2 + array[len(array)-ind-1]*3
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{-1, 2, 1, -8, 2}, 2), expected: -22 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
