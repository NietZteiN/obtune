package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(names string) string {
	parts := strings.Split(names, ",")
	for i, part := range parts {
		parts[i] = strings.Replace(strings.Title(strings.Replace(part, " and", "+", -1)), "+", " and", -1)
	}
	return strings.Join(parts, ", ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("carrot, banana, and strawberry"), expected: "Carrot,  Banana,  and Strawberry" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
