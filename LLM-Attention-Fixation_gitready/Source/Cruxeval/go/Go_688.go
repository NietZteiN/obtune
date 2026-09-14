package f_test

import (
    "testing"
    "fmt"
)

func f(nums []int) []int {
    var l []int
    m := make(map[int]bool)
    for _, i := range nums {
        if _, ok := m[i]; !ok {
            m[i] = true
            l = append(l, i)
        }
    }
    return l
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{3, 1, 9, 0, 2, 0, 8}), expected: []int{3, 1, 9, 0, 2, 8} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
