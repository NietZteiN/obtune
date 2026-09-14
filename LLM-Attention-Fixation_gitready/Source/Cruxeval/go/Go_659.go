package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(bots []string) int {
	clean := []string{}
	for _, username := range bots {
		if username != strings.ToUpper(username) {
			clean = append(clean, username[:2]+username[len(username)-3:])
		}
	}
	return len(clean)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"yR?TAJhIW?n", "o11BgEFDfoe", "KnHdn2vdEd", "wvwruuqfhXbGis"}), expected: 4 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
