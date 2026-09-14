package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, char string) string {
	count := strings.Count(text, strings.Repeat(char, 2))
	return text[count:]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("vzzv2sg", "z"), expected: "zzv2sg" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
