package f_test

import (
	"testing"
	"fmt"
)

func f(lst []int) []int {
	i := 0
	new_list := make([]int, 0, 3)
	for i < len(lst) {
		for j := i + 1; j < len(lst); j++ {
			if lst[i] == lst[j] {
				new_list = append(new_list, lst[i])
				if len(new_list) == 3 {
					return new_list
				}
				break
			}
		}
		i++
	}
	return new_list
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{0, 2, 1, 2, 6, 2, 6, 3, 0}), expected: []int{0, 2, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
