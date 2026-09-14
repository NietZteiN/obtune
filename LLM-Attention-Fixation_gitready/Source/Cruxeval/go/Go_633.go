package f_test

import (
    "testing"
    "fmt"
)

func f(array []int, elem int) int {
    for i := len(array) - 1; i >= 0; i-- {
        if array[i] == elem {
            return len(array) - i - 1
        }
    }
    return -1
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{5, -3, 3, 2}, 2), expected: 0 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
