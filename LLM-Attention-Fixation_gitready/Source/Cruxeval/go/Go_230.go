package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    result := ""
    i := len(text) - 1
    for i >= 0 {
        c := text[i]
        if (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') {
            result += string(c)
        }
        i--
    }
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("102x0zoq"), expected: "qozx" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
