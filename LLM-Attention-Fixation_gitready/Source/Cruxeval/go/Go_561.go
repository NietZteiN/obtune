package main

import (
    "fmt"
    "strings"
    "strconv"
    "testing"
)

func f(text string, digit string) int {
	count := strings.Count(text, digit)
	num, _ := strconv.Atoi(digit)
	return num * count
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("7Ljnw4Lj", "7"), expected: 7 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
