package f_test

import (
    "testing"
    "fmt"
)

func f(text string, char string) string {
    textSlice := []rune(text)
    for i, ch := range textSlice {
        if string(ch) == char {
            textSlice = append(textSlice[:i], textSlice[i+1:]...)
            return string(textSlice)
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
     { actual: candidate("pn", "p"), expected: "n" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
