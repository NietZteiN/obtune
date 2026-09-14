package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string, from_c string, to_c string) string {
	table := strings.NewReplacer(from_c, to_c)
	return table.Replace(s)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("aphid", "i", "?"), expected: "aph?d" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
