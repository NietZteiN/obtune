package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(strand string, zmnc string) int {
	poz := strings.Index(strand, zmnc)
	for poz != -1 {
		strand = strand[poz+1:]
		poz = strings.Index(strand, zmnc)
	}
	return strings.LastIndex(strand, zmnc)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("", "abc"), expected: -1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
