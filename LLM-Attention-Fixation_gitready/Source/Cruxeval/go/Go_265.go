package f_test

import (
    "testing"
    "fmt"
)

func f(d map[int]int, k int) map[int]int {
    new_d := make(map[int]int)
    for key, val := range d {
        if key < k {
            new_d[key] = val
        }
    }
    return new_d
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{1: 2, 2: 4, 3: 3}, 3), expected: map[int]int{1: 2, 2: 4} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
