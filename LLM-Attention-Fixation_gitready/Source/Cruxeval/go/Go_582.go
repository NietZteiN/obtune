package f_test

import (
    "testing"
    "fmt"
)

func f(k int, j int) []int {
    var arr []int
    for i := 0; i < k; i++ {
        arr = append(arr, j)
    }
    return arr
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(7, 5), expected: []int{5, 5, 5, 5, 5, 5, 5} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
