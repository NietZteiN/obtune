package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, c string) string {
	ls := []rune(text)
	if strings.IndexRune(text, []rune(c)[0]) == -1 {
		panic(fmt.Sprintf("Text has no %s", c))
	}
	ls = append(ls[:strings.LastIndex(text, c)], ls[strings.LastIndex(text, c)+1:]...)
	return string(ls)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("uufhl", "l"), expected: "uufh" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
