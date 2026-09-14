package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    new_text := text
    for len(text) > 1 && text[0] == text[len(text)-1] {
        new_text = text
        text = text[1:len(text)-1]
    }
    return new_text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(")"), expected: ")" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
