package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string) string {
    out := ""
    for _, ch := range text {
        if strings.ToUpper(string(ch)) == string(ch) {
            out += strings.ToLower(string(ch))
        } else {
            out += strings.ToUpper(string(ch))
        }
    }
    return out
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(",wPzPppdl/"), expected: ",WpZpPPDL/" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
