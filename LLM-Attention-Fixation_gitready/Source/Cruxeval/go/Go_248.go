package f_test

import (
    "sort"
    "testing"
    "fmt"
)

func f(a []int, b []int) []int {
    sort.Ints(a)
    sort.Sort(sort.Reverse(sort.IntSlice(b)))
    return append(a, b...)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{666}, []int{}), expected: []int{666} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
