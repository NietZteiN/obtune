package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string, x string) string {
    if strings.TrimPrefix(text, x) == text {
        return f(text[1:], x)
    } else {
        return text
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Ibaskdjgblw asdl ", "djgblw"), expected: "djgblw asdl " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
