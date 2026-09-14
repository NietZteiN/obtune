package main

import (
    "fmt"
    "strings"
    "testing"
)

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func f(sequence string, value string) string {
	index := strings.Index(sequence, value)
	i := max(index - len(sequence)/3, 0)
	result := ""
	for j, v := range sequence[i:] {
		if v == '+' {
			result += value
		} else {
			result += string(sequence[i+j])
		}
	}
	return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("hosu", "o"), expected: "hosu" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
