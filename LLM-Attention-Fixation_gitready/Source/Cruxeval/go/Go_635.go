package main

import (
    "fmt"
    "strings"
    "testing"
    "unicode"
)

func f(text string) bool {
	validChars := []rune{'-', '_', '+', '.', '/', ' '}
	text = strings.ToUpper(text)
	for _, char := range text {
		if !unicode.IsLetter(char) && !unicode.IsNumber(char) && !unicode.IsSpace(char) && !containsRune(validChars, char) {
			return false
		}
	}
	return true
}

func containsRune(slice []rune, char rune) bool {
	for _, c := range slice {
		if c == char {
			return true
		}
	}
	return false
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("9.twCpTf.H7 HPeaQ^ C7I6U,C:YtW"), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
