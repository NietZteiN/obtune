package main

import (
    "fmt"
    "testing"
    "sort"
)

func f(array []int) []int {
	var array2 []int
	for _, i := range array {
		if i > 0 {
			array2 = append(array2, i)
		}
	}
	sort.Slice(array2, func(i, j int) bool {
		return array2[i] > array2[j]
	})
	return array2
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{4, 8, 17, 89, 43, 14}), expected: []int{89, 43, 17, 14, 8, 4} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
