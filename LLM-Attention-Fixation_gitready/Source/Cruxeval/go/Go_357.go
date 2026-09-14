package f_test

import (
    "testing"
    "fmt"
)

func f(s string) string {
    r := make([]rune, 0)
    for i := len(s) - 1; i >= 0; i-- {
        r = append(r, []rune(s)[i])
    }
    return string(r)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("crew"), expected: "werc" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
