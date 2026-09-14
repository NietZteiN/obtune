package f_test

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, suffix string) string {
    if len(suffix) > 0 && strings.ContainsRune(text, rune(suffix[len(suffix)-1])) {
        return f(strings.TrimRight(text, string(suffix[len(suffix)-1])), suffix[:len(suffix)-1])
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
     { actual: candidate("rpyttc", "cyt"), expected: "rpytt" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
