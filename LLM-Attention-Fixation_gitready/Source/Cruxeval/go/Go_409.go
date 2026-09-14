package f_test

import (
    "testing"
    "fmt"
)

func f(text string, char string) string {
    if text != "" {
        if len(text) >= len(char) && text[:len(char)] == char {
            text = text[len(char):]
        }
        if len(text) > 1 {
            text = text[:len(text)-1] + string(text[len(text)-1]-32)
        }
    }
    return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("querist", "u"), expected: "querisT" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
