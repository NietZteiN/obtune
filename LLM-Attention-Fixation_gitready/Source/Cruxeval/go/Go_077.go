package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string, character string) string {
    lastIndex := strings.LastIndex(text, character)
    if lastIndex == -1 {
        return ""
    }
    subject := text[lastIndex:]
    count := strings.Count(text, character)
    return strings.Repeat(subject, count)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("h ,lpvvkohh,u", "i"), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
