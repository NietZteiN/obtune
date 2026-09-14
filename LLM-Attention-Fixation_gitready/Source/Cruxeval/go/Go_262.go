package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(nums []int) string {
	score := map[int]string{0: "F", 1: "E", 2: "D", 3: "C", 4: "B", 5: "A", 6: ""}
	result := []string{}
	for _, num := range nums {
		result = append(result, score[num])
	}
	return strings.Join(result, "")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{4, 5}), expected: "BA" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
