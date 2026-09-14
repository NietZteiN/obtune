package f_test

import (
	"sort"
	"testing"
	"fmt"
)

func f(n int) []float64 {
	values := map[int]float64{0: 3, 1: 4.5, 2: '-'}
	res := make(map[float64]int)
	for i, j := range values {
		if i%n != 2 {
			res[j] = n / 2
		}
	}
	keys := make([]float64, 0, len(res))
	for k := range res {
		keys = append(keys, k)
	}
	sort.Float64s(keys)
	return keys
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(12), expected: []float64{3, 4.5} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
