package f_test

import (
    "testing"
    "fmt"
)

func f(text string, space int) string {
    if space < 0 {
        return text
    }
    return fmt.Sprintf("%-*s", len(text)/2+space, text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("sowpf", -7), expected: "sowpf" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
