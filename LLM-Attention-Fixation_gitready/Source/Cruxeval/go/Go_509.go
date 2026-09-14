package f_test

import (
    "testing"
    "fmt"
)

func f(value int, width int) string {
    if value >= 0 {
        return fmt.Sprintf("%0*d", width, value)
    } else {
        return "-" + fmt.Sprintf("%0*d", width, -value)
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(5, 1), expected: "5" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
