package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string, ch string) string {
	sl := s
	if strings.Contains(s, ch) {
		sl = strings.TrimLeft(s, ch)
		if len(sl) == 0 {
			sl = sl + "!?"
		}
	} else {
		return "no"
	}
	return sl
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("@@@ff", "@"), expected: "ff" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
