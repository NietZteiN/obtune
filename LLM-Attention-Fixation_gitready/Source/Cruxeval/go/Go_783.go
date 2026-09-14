package f_test

import (
    "testing"
    "fmt"
)

func f(text string, comparison string) int {
    length := len(comparison)
    if length <= len(text) {
        for i := 0; i < length; i++ {
            if comparison[length-i-1] != text[len(text)-i-1] {
                return i
            }
        }
    }
    return length
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("managed", ""), expected: 0 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
