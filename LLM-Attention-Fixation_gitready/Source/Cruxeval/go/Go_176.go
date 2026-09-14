package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, to_place string) string {
    afterPlaceIndex := strings.Index(text, to_place) + 1
    afterPlace := text[:afterPlaceIndex]
    beforePlace := text[afterPlaceIndex:]
    return afterPlace + beforePlace
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("some text", "some"), expected: "some text" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
