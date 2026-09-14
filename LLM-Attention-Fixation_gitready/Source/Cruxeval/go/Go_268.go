package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(s string, separator string) string {
    for i, char := range s {
        if string(char) == separator {
            s = s[:i] + "/" + s[i+1:]
            return strings.Join(strings.Split(s, ""), " ")
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
     { actual: candidate("h grateful k", " "), expected: "h / g r a t e f u l   k" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
