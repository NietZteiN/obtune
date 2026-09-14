package f_test

import (
    "testing"
    "fmt"
)

func f(a []int) []int {
    b := make([]int, len(a))
    copy(b, a)
    for k := 0; k < len(a)-1; k += 2 {
        b = append(b[:k+1], append([]int{b[k]}, b[k+1:]...)...)
    }
    b = append(b, b[0])
    return b
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{5, 5, 5, 6, 4, 9}), expected: []int{5, 5, 5, 5, 5, 5, 6, 4, 9, 5} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
