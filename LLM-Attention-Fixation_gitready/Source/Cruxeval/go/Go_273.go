package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(name string) string {
	newName := ""
	runes := []rune(name)
	for i := len(runes) - 1; i >= 0; i-- {
		n := runes[i]
		if string(n) != "." && strings.Count(newName, ".") < 2 {
			newName = string(n) + newName
		} else {
			break
		}
	}
	return newName
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(".NET"), expected: "NET" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
