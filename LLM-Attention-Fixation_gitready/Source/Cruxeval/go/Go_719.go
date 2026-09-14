package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(code string) string {
	lines := strings.Split(code, "]")
	var result []string
	level := 0
	for _, line := range lines {
		result = append(result, string(line[0])+" "+strings.Repeat("  ", level)+line[1:])
		level += strings.Count(line, "{") - strings.Count(line, "}")
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
     { actual: candidate("if (x) {y = 1;} else {z = 1;}"), expected: "i f (x) {y = 1;} else {z = 1;}" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
