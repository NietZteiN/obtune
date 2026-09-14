package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(names []string, excluded string) []string {
	for i := 0; i < len(names); i++ {
		if strings.Contains(names[i], excluded) {
			names[i] = strings.Replace(names[i], excluded, "", -1)
		}
	}
	return names
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"avc  a .d e"}, ""), expected: []string{"avc  a .d e"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
