package f_test

import (
	"testing"
	"fmt"
)

func f(items []int) []int {
	var oddPositioned []int
	for len(items) > 0 {
		minIndex := 0
		for i, val := range items {
			if val < items[minIndex] {
				minIndex = i
			}
		}
		items = append(items[:minIndex], items[minIndex+1:]...)
		item := items[minIndex]
		items = append(items[:minIndex], items[minIndex+1:]...)
		oddPositioned = append(oddPositioned, item)
	}
	return oddPositioned
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 3, 4, 5, 6, 7, 8}), expected: []int{2, 4, 6, 8} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
