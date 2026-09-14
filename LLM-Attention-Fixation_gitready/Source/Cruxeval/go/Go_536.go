package f_test

import (
    "testing"
    "fmt"
)

func f(cat string) int {
    digits := 0
    for _, char := range cat {
        if char >= '0' && char <= '9' {
            digits++
        }
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
     { actual: candidate("C24Bxxx982ab"), expected: 5 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
