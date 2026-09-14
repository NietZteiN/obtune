package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, new_value string, index int) string {
	key := strings.NewReplacer(string(text[index]), new_value)
	return key.Replace(text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("spain", "b", 4), expected: "spaib" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
