package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, ch string) string {
	lines := strings.Split(text, "\n")
	var result []string

	for _, line := range lines {
		if len(line) > 0 && string(line[0]) == ch {
			result = append(result, strings.ToLower(line))
		} else {
			result = append(result, strings.ToUpper(line))
		}
	}

	return strings.Join(result, "\n")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("t\nza\na", "t"), expected: "t\nZA\nA" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
