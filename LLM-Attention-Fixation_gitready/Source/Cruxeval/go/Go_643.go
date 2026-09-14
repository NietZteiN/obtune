package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, suffix string) string {
	if strings.HasSuffix(text, suffix) {
		text = text[:len(text)-1] + strings.ToUpper(text[len(text)-1:])
	}
	return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("damdrodm", "m"), expected: "damdrodM" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
