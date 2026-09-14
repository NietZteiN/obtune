package f_test

import (
    "testing"
    "fmt"
)

func f(num int, name string) string {
    return fmt.Sprintf("quiz leader = %s, count = %d", name, num)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(23, "Cornareti"), expected: "quiz leader = Cornareti, count = 23" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
