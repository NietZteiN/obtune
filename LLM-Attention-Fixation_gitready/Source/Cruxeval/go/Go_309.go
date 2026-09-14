package f_test

import (
    "testing"
    "fmt"
)

func f(text string, suffix string) string {
    text += suffix
    for len(text) >= len(suffix) && text[len(text)-len(suffix):] == suffix {
        text = text[:len(text)-1]
    }
    return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("faqo osax f", "f"), expected: "faqo osax " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
