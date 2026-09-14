package f_test

import (
    "testing"
    "fmt"
)

func f(temp int, timeLimit int) string {
    s := timeLimit / temp
    e := timeLimit % temp
    if s > 1 {
        return fmt.Sprintf("%d %d", s, e)
    }
    return fmt.Sprintf("%d oC", e)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(1, 1234567890), expected: "1234567890 0" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
