package f_test

import (
	"testing"
	"fmt"
	"strings"
)

func f(t string) string {
	a, sep, b := t, "-", ""
	parts := strings.Split(t, "-")
	if len(parts) > 1 {
		a = parts[0]
		b = parts[1]
	}
	if len(b) == len(a) {
		return "imbalanced"
	}
	return a + strings.Replace(b, sep, "", -1)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("fubarbaz"), expected: "fubarbaz" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
