package f_test

import (
    "testing"
    "fmt"
    "strings"
    "unicode"
)

func f(text string) string {
    for _, r := range text {
        if !unicode.IsUpper(r) && unicode.IsLetter(r) {
            return strings.Title(strings.ToLower(text))
        }
    }
    return strings.ToLower(text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("PermissioN is GRANTed"), expected: "Permission Is Granted" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
