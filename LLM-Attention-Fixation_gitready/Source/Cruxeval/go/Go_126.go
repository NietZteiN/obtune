package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string) string {
    s := strings.LastIndex(text, "o")
    if s == -1 {
        return "-" + text
    }
    return text[:s+1] + text[s+1:]
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("kkxkxxfck"), expected: "-kkxkxxfck" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
