package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, sep string, maxsplit int) string {
	splitted := strings.Split(text, sep)
	reversed := make([]string, len(splitted))
	for i, v := range splitted {
		reversed[len(splitted)-1-i] = v
	}
	newSplitted := append(reversed[:len(splitted)/2], splitted[len(splitted)/2:]...)
	return strings.Join(newSplitted, sep)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("ertubwi", "p", 5), expected: "ertubwi" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
