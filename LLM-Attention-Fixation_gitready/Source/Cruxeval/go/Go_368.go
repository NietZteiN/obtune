package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(myString string, numbers []int) string {
	var arr []string
	for _, num := range numbers {
		arr = append(arr, fmt.Sprintf("%0*s", num, myString))
	}
	return strings.Join(arr, " ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("4327", []int{2, 8, 9, 2, 7, 1}), expected: "4327 00004327 000004327 4327 0004327 4327" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
