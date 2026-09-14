package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, wrong string, right string) string {
    new_text := strings.Replace(text, wrong, right, -1)
    return strings.ToUpper(new_text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("zn kgd jw lnt", "h", "u"), expected: "ZN KGD JW LNT" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
