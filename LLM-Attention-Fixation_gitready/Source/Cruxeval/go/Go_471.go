package f_test

import (
    "testing"
    "fmt"
)

func f(val string, text string) int {
    indices := []int{}
    for index, char := range text {
        if string(char) == val {
            indices = append(indices, index)
        }
    }
    if len(indices) == 0 {
        return -1
    } else {
        return indices[0]
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("o", "fnmart"), expected: -1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
