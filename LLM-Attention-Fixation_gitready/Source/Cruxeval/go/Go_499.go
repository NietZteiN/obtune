package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string, length int, fillChar string) string {
    if len(text) >= length {
        return text
    }
    var sb strings.Builder
    padLength := length - len(text)
    fillLen := padLength >> 1
    leftFillLen := fillLen + padLength%2
    sb.WriteString(strings.Repeat(fillChar, leftFillLen))
    sb.WriteString(text)
    sb.WriteString(strings.Repeat(fillChar, fillLen))
    return sb.String()
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("magazine", 25, "."), expected: ".........magazine........" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
