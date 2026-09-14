package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(address string) string {
	suffixStart := strings.Index(address, "@") + 1
	if strings.Count(address[suffixStart:], ".") > 1 {
		splitAddress := strings.Split(address, "@")[1]
		splitParts := strings.Split(splitAddress, ".")[:2]
		suffixToRemove := strings.Join(splitParts, ".")
		address = strings.TrimSuffix(address, suffixToRemove)
	}
	return address
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("minimc@minimc.io"), expected: "minimc@minimc.io" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
