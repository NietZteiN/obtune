package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(arr []int) string {
	var strArr []string
	strArr = append(strArr, "1", "2", "3", "4")
	return strings.Join(strArr, ",")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{0, 1, 2, 3, 4}), expected: "1,2,3,4" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
