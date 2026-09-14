package main

import (
    "fmt"
    "strings"
    "testing"
)

func findIndex(array []string, s string) int {
	for i, val := range array {
		if val == s {
			return i
		}
	}
	return -1
}

func f(array []string, arr []string) []string {
	result := []string{}
	for _, s := range arr {
		for _, l := range strings.Split(s, array[findIndex(array, s)]) {
			if l != "" {
				result = append(result, l)
			}
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
     { actual: candidate([]string{}, []string{}), expected: []string{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
