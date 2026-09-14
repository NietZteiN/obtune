package f_test

import (
    "testing"
    "fmt"
)

func f(char_freq map[string]int) map[string]int {
    result := make(map[string]int)
    for k, v := range char_freq {
        result[k] = v / 2
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
     { actual: candidate(map[string]int{"u": 20, "v": 5, "b": 7, "w": 3, "x": 3}), expected: map[string]int{"u": 10, "v": 2, "b": 3, "w": 1, "x": 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
