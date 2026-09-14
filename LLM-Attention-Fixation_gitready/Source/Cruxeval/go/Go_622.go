package f_test

import (
	"strings"
	"testing"
	"fmt"
)

func f(s string) string {
	left, sep, right := lastPartition(s, ".")
	new := join([]string{right, left}, sep)
	_, sep, _ = lastPartition(new, ".")
	return replace(new, sep, ", ")
}

func lastPartition(s, sep string) (string, string, string) {
	lastIndex := strings.LastIndex(s, sep)
	if lastIndex == -1 {
		return s, "", ""
	}
	return s[:lastIndex], sep, s[lastIndex+len(sep):]
}

func join(s []string, sep string) string {
	return strings.Join(s, sep)
}

func replace(s, old, new string) string {
	return strings.Replace(s, old, new, -1)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("galgu"), expected: ", g, a, l, g, u, " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
