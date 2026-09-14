package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(txt string, marker int) string {
    var a []string
    lines := strings.Split(txt, "\n")
    for _, line := range lines {
        a = append(a, center(line, marker))
    }
    return strings.Join(a, "\n")
}

func center(s string, w int) string {
	for len(s) < w {
		switch {
		case len(s)%2 == 0:
			s = " " + s + " "
		default:
			s = " " + s
		}
	}
	return s
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("#[)[]>[^e>\n 8", -5), expected: "#[)[]>[^e>\n 8" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
