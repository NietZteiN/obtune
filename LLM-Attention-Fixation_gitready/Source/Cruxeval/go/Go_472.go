package main

import (
    "fmt"
    "testing"
    "unicode"
)

func f(text string) []int {
	d := make(map[rune]int)
	for _, char := range text {
		if char == '-' {
			continue
		}
		char = unicode.ToLower(char)
		d[char]++
	}

	var items []int
	for _, val := range d {
		items = append(items, val)
	}

	return items
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("x--y-z-5-C"), expected: []int{1, 1, 1, 1, 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
