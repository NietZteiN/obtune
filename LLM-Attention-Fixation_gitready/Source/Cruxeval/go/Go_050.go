package f_test

import (
    "testing"
    "fmt"
)

func f(lst []string) []int {
    lst = []string{}
    lst = append(lst, make([]string, len(lst)+1)...)
    res := make([]int, len(lst))
    for i := range res {
        res[i] = 1
    }
    return res
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"a", "c", "v"}), expected: []int{1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
