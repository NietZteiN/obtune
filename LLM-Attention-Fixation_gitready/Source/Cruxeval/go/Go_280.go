package f_test

import (
    "testing"
    "fmt"
    "strings"
)

var g, field string

func f(text string) string {
    field = strings.ReplaceAll(text, " ", "")
    g = strings.ReplaceAll(text, "0", " ")
    text = strings.ReplaceAll(text, "1", "i")

    return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("00000000 00000000 01101100 01100101 01101110"), expected: "00000000 00000000 0ii0ii00 0ii00i0i 0ii0iii0" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
