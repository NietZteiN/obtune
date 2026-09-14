package f_test

import (
    "testing"
    "fmt"
)

func f(n int, m int) []int {
    arr := make([]int, n)
    for i := 1; i <= n; i++ {
        arr[i-1] = i
    }
    for i := 0; i < m; i++ {
        arr = nil
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
     { actual: candidate(1, 3), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
