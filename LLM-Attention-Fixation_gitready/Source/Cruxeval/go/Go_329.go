package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string) bool {
    for i := 1; i < len(text); i++ {
        if text[i] == strings.ToUpper(string(text[i]))[0] && text[i-1] == strings.ToLower(string(text[i-1]))[0] {
            return true
        }
    }
    return false
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("jh54kkk6"), expected: true },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
