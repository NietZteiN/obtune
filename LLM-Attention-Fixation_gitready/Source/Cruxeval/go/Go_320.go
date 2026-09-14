package main

import (
    "fmt"
    "strings"
    "testing"
)

func swapCase(text string) string {
	var result strings.Builder
	for _, char := range text {
		if char >= 'a' && char <= 'z' {
			result.WriteRune(char - 32) // Convert lowercase to uppercase
		} else if char >= 'A' && char <= 'Z' {
			result.WriteRune(char + 32) // Convert uppercase to lowercase
		} else {
			result.WriteRune(char) // Keep non-alphabetic characters as they are
		}
	}
	return result.String()
}

func f(text string) string {
	index := 1
	for index < len(text) {
		if text[index] != text[index-1] {
			index++
		} else {
			text1 := text[:index]
			text2 := swapCase(text[index:])
			return text1 + text2
		}
	}
	return swapCase(text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("USaR"), expected: "usAr" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
