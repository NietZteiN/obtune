package f_test

import (
	"testing"
	"fmt"
	"strings"
)

func f(text string) string {
	ls := []rune(text)
	for i := 0; i < len(ls); i++ {
		if ls[i] != '+' {
			ls = append(ls[:i], append([]rune{'*', '+'}, ls[i:]...)...)
			break
		}
	}
	return strings.Join(strings.Split(string(ls), ""), "+")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("nzoh"), expected: "*+++n+z+o+h" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
