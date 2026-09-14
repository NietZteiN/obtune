package f_test

import (
    "testing"
    "fmt"
)

func f(s string) string {
    r := []rune(s)
    result := ""
    for i := len(r) - 1; i >= 0; i-- {
        if r[i] != ' ' {
            result += string(r[i])
        }
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
     { actual: candidate("ab        "), expected: "ba" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
