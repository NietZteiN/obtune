package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(alphabet string, s string) []string {
	var result []string
	for _, x := range alphabet {
		if strings.Contains(s, strings.ToUpper(string(x))) {
			result = append(result, string(x))
		}
	}

	if strings.ToUpper(s) == s {
		result = append(result, "all_uppercased")
	}

	return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("abcdefghijklmnopqrstuvwxyz", "uppercased # % ^ @ ! vz."), expected: []string{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
