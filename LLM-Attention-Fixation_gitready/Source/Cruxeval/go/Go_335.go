package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, to_remove string) string {
	new_text := []rune(text)
	if strings.ContainsRune(text, []rune(to_remove)[0]) {
		index := strings.Index(text, to_remove)
		new_text = append(new_text[:index], append([]rune{'?'}, new_text[index+1:]...)...)
		new_text = append(new_text[:index], new_text[index+1:]...)
	}
	return string(new_text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("sjbrlfqmw", "l"), expected: "sjbrfqmw" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
