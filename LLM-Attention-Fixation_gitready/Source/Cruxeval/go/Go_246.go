package f_test

import (
    "testing"
    "fmt"
)

func f(haystack string, needle string) int {
    for i := len(haystack) - len(needle); i >= 0; i-- {
        if haystack[i:] == needle {
            return i
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
     { actual: candidate("345gerghjehg", "345"), expected: -1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
