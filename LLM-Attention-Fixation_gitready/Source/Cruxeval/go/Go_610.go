package f_test

import (
    "testing"
    "fmt"
)

func f(keys []int, value int) map[int]int {
    d := make(map[int]int)
    for _, k := range keys {
        d[k] = value
    }
    for i := len(keys) - 1; i >= 0; i-- {
        if d[keys[i]] == d[i+1] {
            delete(d, i+1)
        }
    }
    return d
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2, 1, 1}, 3), expected: map[int]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
