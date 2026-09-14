package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    new_text := make([]rune, len(text))
    for i, c := range text {
        if c >= '0' && c <= '9' {
            new_text[i] = c
        } else {
            new_text[i] = '*'
        }
    }
    return string(new_text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("5f83u23saa"), expected: "5*83*23***" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
