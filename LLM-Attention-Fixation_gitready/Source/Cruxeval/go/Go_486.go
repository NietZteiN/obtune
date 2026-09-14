package f_test

import (
    "testing"
    "fmt"
)

func f(dic map[int]int) map[int]int {
    dic_op := make(map[int]int)
    for key, val := range dic {
        dic_op[key] = val * val
    }
    return dic_op
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{1: 1, 2: 2, 3: 3}), expected: map[int]int{1: 1, 2: 4, 3: 9} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
