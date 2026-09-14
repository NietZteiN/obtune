package f_test

import (
    "testing"
    "fmt"
)

func f(xs []int) []int {
    new_x := xs[0] - 1
    xs = append(xs[:0], xs[1:]...)
    for new_x <= xs[0] {
        xs = xs[1:]
        new_x--
    }
    xs = append([]int{new_x}, xs...)
    return xs
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{6, 3, 4, 1, 2, 3, 5}), expected: []int{5, 3, 4, 1, 2, 3, 5} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
