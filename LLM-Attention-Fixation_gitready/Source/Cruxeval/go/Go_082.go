package f_test

import (
    "testing"
    "fmt"
)

func f(a string, b string, c string, d string) string {
    if a != "" {
        return b
    } else {
        return d
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("CJU", "BFS", "WBYDZPVES", "Y"), expected: "BFS" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
