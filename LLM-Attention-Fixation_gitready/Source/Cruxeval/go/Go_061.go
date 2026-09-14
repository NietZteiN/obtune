package main

import (
    "unicode/utf8"
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	texts := strings.Fields(text)
	if len(texts) > 0 {
		var xtexts []string
		for _, t := range texts {
			if utf8.ValidString(t) && t != "nada" && t != "0" {
				xtexts = append(xtexts, t)
			}
		}
		if len(xtexts) > 0 {
			maxLength := 0
			maxLengthText := ""
			for _, t := range xtexts {
				if len(t) > maxLength {
					maxLength = len(t)
					maxLengthText = t
				}
			}
			return maxLengthText
		}
	}
	return "nada"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(""), expected: "nada" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
