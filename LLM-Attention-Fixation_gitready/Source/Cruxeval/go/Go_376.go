package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    for i := 0; i < len(text); i++ {
        if text[:i] == "two" {
            return text[i:]
        }
    }
    return "no"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("2two programmers"), expected: "no" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
