package f_test

import (
    "testing"
    "fmt"
)

func f(dict map[int]int) map[int]int {
    result := make(map[int]int)
    for k, v := range dict {
        if _, ok := dict[v]; !ok {
            result[k] = v
        }
    }
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{-1: -1, 5: 5, 3: 6, -4: -4}), expected: map[int]int{3: 6} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
