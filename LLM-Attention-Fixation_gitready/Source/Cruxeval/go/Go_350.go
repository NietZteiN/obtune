package f_test

import (
    "testing"
    "fmt"
)

func f(d map[string]int) []int {
    size := len(d)
    v := make([]int, size)
    if size == 0 {
        return v
    }
    i := 0
    for _, e := range d {
        v[i] = e
        i++
    }
    return v
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"a": 1, "b": 2, "c": 3}), expected: []int{1, 2, 3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
