package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(l []string, c string) string {
	return strings.Join(l, c)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"many", "letters", "asvsz", "hello", "man"}, ""), expected: "manylettersasvszhelloman" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
