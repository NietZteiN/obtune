package f_test

import (
	"testing"
	"fmt"
)

func f(numbers []int, elem int, idx int) []int {
	if idx >= len(numbers) {
		return append(numbers, elem)
	}
	numbers = append(numbers[:idx+1], numbers[idx:]...)
	numbers[idx] = elem
	return numbers
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 3}, 8, 5), expected: []int{1, 2, 3, 8} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
