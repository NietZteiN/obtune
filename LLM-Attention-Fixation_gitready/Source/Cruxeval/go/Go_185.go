package f_test

import (
    "testing"
    "fmt"
)

func f(L []int) []int {
    N := len(L)
    for k := 1; k <= N/2; k++ {
        i := k - 1
        j := N - k
        for i < j {
            // swap elements:
            L[i], L[j] = L[j], L[i]
            // update i, j:
            i++
            j--
        }
    }
    return L
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{16, 14, 12, 7, 9, 11}), expected: []int{11, 14, 7, 12, 9, 16} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
