package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string, num int) string {
    req := num - len(text)
    text = fmt.Sprintf("%*s", num, text)
    text = strings.Replace(text, " ", "*", -1)
    return text[req/2 : len(text) - req/2]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("a", 19), expected: "*" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
