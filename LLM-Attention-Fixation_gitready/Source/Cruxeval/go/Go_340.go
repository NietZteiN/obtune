package main

import (
    "fmt"
    "strings"
    "testing"
    "sort"
)

func f(text string) string {
	uppercaseIndex := strings.Index(text, "A")
	if uppercaseIndex >= 0 {
		return text[:uppercaseIndex] + text[strings.Index(text, "a")+1:]
	} else {
		runes := []rune(text)
		sort.Slice(runes, func(i, j int) bool { return runes[i] < runes[j] })
		return string(runes)
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("E jIkx HtDpV G"), expected: "   DEGHIVjkptx" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
