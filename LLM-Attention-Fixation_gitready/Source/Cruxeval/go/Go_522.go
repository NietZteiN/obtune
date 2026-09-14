package f_test

import (
    "testing"
    "fmt"
)

func f(numbers []int) []float64 {
    floats := make([]float64, len(numbers))
    for i, n := range numbers {
        floats[i] = float64(n) - float64(int(n))
    }
    for _, f := range floats {
        if f == 1 {
            return floats
        }
    }
    return []float64{}
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119}), expected: []float64{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
