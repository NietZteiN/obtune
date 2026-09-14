package f_test

import (
    "testing"
    "fmt"
)

func f(text string, prefix string) string {
    idx := 0
    for _, letter := range prefix {
        if text[idx] != byte(letter) {
            return ""
        }
        idx++
    }
    return text[idx:]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("bestest", "bestest"), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
