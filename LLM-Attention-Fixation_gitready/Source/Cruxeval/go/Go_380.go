package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string, delimiter string) string {
    text = text[:strings.LastIndex(text, delimiter)] + text[strings.LastIndex(text, delimiter)+len(delimiter):]
    return text
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("xxjarczx", "x"), expected: "xxjarcz" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
