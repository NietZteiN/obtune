package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	t := 5
	var tab []string
	for _, r := range text {
		if r == 'a' || r == 'e' || r == 'i' || r == 'o' || r == 'u' || r == 'y' {
			tab = append(tab, strings.Repeat(strings.ToUpper(string(r)), t))
		} else {
			tab = append(tab, strings.Repeat(string(r), t))
		}
	}
	return strings.Join(tab, " ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("csharp"), expected: "ccccc sssss hhhhh AAAAA rrrrr ppppp" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
