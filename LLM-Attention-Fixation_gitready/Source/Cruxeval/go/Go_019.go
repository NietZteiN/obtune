package main

import (
    "fmt"
    "strconv"
    "testing"
)

func f(x string, y string) string {
	tmp := ""
	for i := len(y) - 1; i >= 0; i-- {
		if y[i] == '9' {
			tmp += "0"
		} else {
			tmp += "9"
		}
	}

	if _, err1 := strconv.Atoi(x); err1 == nil {
		if _, err2 := strconv.Atoi(tmp); err2 == nil {
			return x + tmp
		}
	}

	return x
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("", "sdasdnakjsda80"), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
