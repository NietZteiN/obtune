package f_test

import (
    "testing"
    "fmt"
)

func f(a []int) []int {
    if len(a) >= 2 && a[0] > 0 && a[1] > 0 {
        for i, j := 0, len(a)-1; i < j; i, j = i+1, j-1 {
            a[i], a[j] = a[j], a[i]
        }
        return a
    }
    a = append(a, 0)
    return a
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{}), expected: []int{0} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
