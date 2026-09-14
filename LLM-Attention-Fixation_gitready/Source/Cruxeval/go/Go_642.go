package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    i := 0
    for i < len(text) && text[i] == ' ' {
        i++
    }
    if i == len(text) {
        return "space"
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
     { actual: candidate("     "), expected: "space" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
