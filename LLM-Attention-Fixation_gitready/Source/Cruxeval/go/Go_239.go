package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string, froms string) string {
    text = strings.TrimLeft(text, froms)
    text = strings.TrimRight(text, froms)
    return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("0 t 1cos ", "st 0	\n  "), expected: "1co" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
