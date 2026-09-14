package f_test

import (
    "testing"
    "strings"
    "fmt"
)

func f(st string) string {
    if st[0] == '~' {
        e := strings.Repeat("s", 10 - len(st)) + st
        return f(e)
    } else {
        return strings.Repeat("n", 10 - len(st)) + st
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("eqe-;ew22"), expected: "neqe-;ew22" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
