package f_test

import (
    "testing"
    "fmt"
)

func f(li []string) []int {
    counts := make([]int, len(li))
    for i, val := range li {
        counts[i] = 0
        for _, v := range li {
            if val == v {
                counts[i]++
            }
        }
    }
    return counts
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"k", "x", "c", "x", "x", "b", "l", "f", "r", "n", "g"}), expected: []int{1, 3, 1, 3, 3, 1, 1, 1, 1, 1, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
