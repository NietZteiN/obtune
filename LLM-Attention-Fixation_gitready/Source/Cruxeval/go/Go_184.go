package f_test

import (
    "testing"
    "fmt"
)

func f(digits []int) []int {
    for i, j := 0, len(digits)-1; i < j; i, j = i+1, j-1 {
        digits[i], digits[j] = digits[j], digits[i]
    }
    if len(digits) < 2 {
        return digits
    }
    for i := 0; i < len(digits)-1; i += 2 {
        digits[i], digits[i+1] = digits[i+1], digits[i]
    }
    return digits
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1, 2}), expected: []int{1, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
