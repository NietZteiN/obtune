package f_test

import (
	"testing"
	"fmt"
)

func f(dic map[int]int) map[int]int {
	d := make(map[int]int)
	keys := make([]int, 0, len(dic))
	for k := range dic {
		keys = append(keys, k)
	}
	for i, key := range keys {
		d[key] = dic[keys[i]]
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
     { actual: candidate(map[int]int{}), expected: map[int]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
