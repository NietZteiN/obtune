package f_test

import (
    "testing"
    "fmt"
)

func f(lst []int) []int {
    var res []int
    for i := range lst {
        if lst[i]%2 == 0 {
            res = append(res, lst[i])
        }
    }
    
    return append([]int(nil), lst...)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 3, 4}), expected: []int{1, 2, 3, 4} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
