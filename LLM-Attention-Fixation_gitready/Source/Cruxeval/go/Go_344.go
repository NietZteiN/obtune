package f_test

import (
	"testing"
	"fmt"
	"sort"
)

func f(lst []int) []int {
	new_list := make([]int, len(lst))
	copy(new_list, lst)
	sort.Ints(new_list)
	for i, j := 0, len(new_list)-1; i < j; i, j = i+1, j-1 {
		new_list[i], new_list[j] = new_list[j], new_list[i]
	}
	return lst
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{6, 4, 2, 8, 15}), expected: []int{6, 4, 2, 8, 15} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
