package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, rules []string) string {
	for _, rule := range rules {
		if rule == "@" {
			text = reverseString(text)
		} else if rule == "~" {
			text = strings.ToUpper(text)
		} else if len(text) > 0 && text[len(text)-1] == rule[0] {
			text = text[:len(text)-1]
		}
	}
	return text
}

func reverseString(s string) string {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("hi~!", []string{"~", "`", "!", "&"}), expected: "HI~" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
