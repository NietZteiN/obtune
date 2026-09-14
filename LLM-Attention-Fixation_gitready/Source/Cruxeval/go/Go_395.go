package f_test

import (
    "testing"
    "fmt"
)

func f(s string) int {
    for i, char := range s {
        if char >= '0' && char <= '9' {
            if char == '0' {
                return i + 1
            }
            return i
        } else if char == '0' {
            return -1
        }
    }
    return -1
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("11"), expected: 0 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
