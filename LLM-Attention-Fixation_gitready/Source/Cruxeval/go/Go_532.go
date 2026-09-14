package f_test

import (
    "testing"
    "fmt"
)

func f(n int, array []int) [][]int {
    final := [][]int{append([]int{}, array...)}
    for i := 0; i < n; i++ {
        arr := append([]int{}, array...)
        arr = append(arr, final[len(final)-1]...)
        final = append(final, arr)
    }
    return final
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(1, []int{1, 2, 3}), expected: [][]int{[]int{1, 2, 3}, []int{1, 2, 3, 1, 2, 3}} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
