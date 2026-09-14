package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    new_text := make([]byte, 0)
    for _, char := range text {
        if char >= 'A' && char <= 'Z' {
            mid := len(new_text) / 2
            new_text = append(new_text[:mid], append([]byte{byte(char)}, new_text[mid:]...)...)
        }
    }
    if len(new_text) == 0 {
        new_text = []byte{'-'}
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
     { actual: candidate("String matching is a big part of RexEx library."), expected: "RES" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
