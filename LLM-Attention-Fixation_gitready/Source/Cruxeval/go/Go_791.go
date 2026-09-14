package f_test

import (
    "testing"
    "fmt"
)

func f(integer int, n int) string {
    i := 1
    text := fmt.Sprintf("%d", integer)
    for i + len(text) < n {
        i += len(text)
    }
    return fmt.Sprintf("%0*d", i+len(text), integer)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(8999, 2), expected: "08999" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
