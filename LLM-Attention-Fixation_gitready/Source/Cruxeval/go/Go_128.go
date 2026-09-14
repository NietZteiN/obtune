package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
    odd := ""
    even := ""
    for i, c := range text {
        if i % 2 == 0 {
            even += string(c)
        } else {
            odd += string(c)
        }
    }
    return even + strings.ToLower(odd)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Mammoth"), expected: "Mmohamt" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
