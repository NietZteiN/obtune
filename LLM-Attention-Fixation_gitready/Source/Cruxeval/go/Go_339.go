package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, elem int) int {
    elemStr := fmt.Sprintf("%d", elem)
    d := 0
    for _, i := range array {
        if fmt.Sprintf("%d", i) == elemStr {
            d++
        }
    }
    return d
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{-1, 2, 1, -8, -8, 2}, 2), expected: 2 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
