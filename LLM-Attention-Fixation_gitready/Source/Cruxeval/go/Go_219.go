package f_test

import (
    "strings"
    "testing"
    "fmt"
)

func f(s1 string, s2 string) bool {
    for len(s1) <= len(s2) {
        if strings.Contains(s1, s2) {
            return true
        }
        s1 += string(s1[0])
    }
    return false
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Hello", ")"), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
