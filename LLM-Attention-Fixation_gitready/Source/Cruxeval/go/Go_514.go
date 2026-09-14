package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	words := strings.Split(text, " ")
	for _, item := range words {
		text = strings.ReplaceAll(text, "-"+item, " ")
		text = strings.ReplaceAll(text, item+"-", " ")
	}
	return strings.Trim(text, "-")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("-stew---corn-and-beans-in soup-.-"), expected: "stew---corn-and-beans-in soup-." },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
