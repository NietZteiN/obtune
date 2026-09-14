package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string) []string {
    ls := strings.Fields(text)
    lines := make([]string, 0)
    for i := 0; i < len(ls); i += 3 {
        lines = append(lines, ls[i])
    }
    res := make([]string, 0)
    for i := 0; i < 2; i++ {
        ln := make([]string, 0)
        for j := 1; j < len(ls); j += 3 {
            ln = append(ln, ls[j])
        }
        if (3 * i + 1) < len(ln) {
            res = append(res, strings.Join(ln[3*i:3*(i+1)], " "))
        }
    }
    return append(lines, res...)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("echo hello!!! nice!"), expected: []string{"echo"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
