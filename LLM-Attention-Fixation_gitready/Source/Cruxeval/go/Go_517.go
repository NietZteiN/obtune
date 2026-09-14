package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    for i := len(text) - 1; i >= 0; i-- {
        if text[i] < 65 || text[i] > 90 {
            return text[0:i]
        }
    }
    return ""
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("SzHjifnzog"), expected: "SzHjifnzo" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
