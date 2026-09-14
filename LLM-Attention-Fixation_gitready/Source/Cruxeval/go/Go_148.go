package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(forest string, animal string) string {
	index := strings.Index(forest, animal)
	result := []rune(forest)
	for index < len(forest)-1 {
		result[index] = rune(forest[index+1])
		index++
	}
	if index == len(forest)-1 {
		result[index] = '-'
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
     { actual: candidate("2imo 12 tfiqr.", "m"), expected: "2io 12 tfiqr.-" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
