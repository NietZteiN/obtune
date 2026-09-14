package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(str string, toget string) string {
    if strings.HasPrefix(str, toget) {
        return str[len(toget):]
    } else {
        return str
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("fnuiyh", "ni"), expected: "fnuiyh" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
