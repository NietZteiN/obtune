package f_test

import (
    "testing"
    "fmt"
)

func f(s string, x string) string {
    count := 0
    for len(s) >= len(x) && s[:len(x)] == x {
        s = s[len(x):]
        count += len(x)
    }
    return s
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("If you want to live a happy life! Daniel", "Daniel"), expected: "If you want to live a happy life! Daniel" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
