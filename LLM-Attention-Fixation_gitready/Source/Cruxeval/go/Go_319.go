package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(needle string, haystack string) int {
	count := 0
	for {
		if index := strings.Index(haystack, needle); index != -1 {
			haystack = haystack[:index] + haystack[index+len(needle):]
			count++
		} else {
			break
		}
	}
	return count
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("a", "xxxaaxaaxx"), expected: 4 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
