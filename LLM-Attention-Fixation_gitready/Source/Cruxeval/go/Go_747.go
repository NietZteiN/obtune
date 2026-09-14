package f_test

import (
    "fmt"
    "testing"
    "unicode"
)

func isNumeric(s string) bool {
    for _, r := range s {
        if !unicode.IsDigit(r) {
            return false
        }
    }
    return true
}

func f(text string) bool {
    if text == "42.42" {
        return true
    }

    for i := 3; i < len(text)-3; i++ {
        if text[i] == '.' && isNumeric(text[i-3:]) && isNumeric(text[:i]) {
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
     { actual: candidate("123E-10"), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
