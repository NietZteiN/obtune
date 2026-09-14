package f_test

import (
    "testing"
    "fmt"
)

func f(items []string, target string) int {
    for i, item := range items {
        if item == target {
            return i
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
     { actual: candidate([]string{"1", "+", "-", "**", "//", "*", "+"}, "**"), expected: 3 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
