package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    newText := []rune(text)
    for i := len(newText) - 1; i >= 0; i-- {
        if newText[i] == ' ' {
            newText[i] = rune('&')
            newText = append(newText[:i+1], append([]rune("nbsp;"), newText[i+1:]...)...)
        }
    }
    return string(newText)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("   "), expected: "&nbsp;&nbsp;&nbsp;" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
