package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(vectors [][]int) [][]int {
	sortedVecs := make([][]int, 0)

	for _, vec := range vectors {
		sortedVec := make([]int, len(vec))
		copy(sortedVec, vec)
		sort.Ints(sortedVec)
		sortedVecs = append(sortedVecs, sortedVec)
	}

	return sortedVecs
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([][]int{}), expected: [][]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
