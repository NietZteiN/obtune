package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, char string) string {
	index := strings.LastIndex(text, char)
	result := []rune(text)
	for index > 0 {
		result[index] = result[index-1]
		result[index-1] = rune(char[0])
		index -= 2
	}
	return string(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("qpfi jzm", "j"), expected: "jqjfj zm" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
