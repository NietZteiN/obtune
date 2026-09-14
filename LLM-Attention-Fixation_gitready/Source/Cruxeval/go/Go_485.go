package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(tokens string) string {
	tokenSlice := strings.Split(tokens, " ")
	if len(tokenSlice) == 2 {
		tokenSlice[0], tokenSlice[1] = tokenSlice[1], tokenSlice[0]
	}
	result := fmt.Sprintf("%-5s %-5s", tokenSlice[0], tokenSlice[1])
	return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("gsd avdropj"), expected: "avdropj gsd  " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
