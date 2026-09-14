package f_test

import (
    "testing"
    "fmt"
)

func f(lines []string) []string {
    for i := range lines {
        lines[i] = fmt.Sprintf("%*s", len(lines[len(lines)-1]), lines[i])
    }
    return lines
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"dZwbSR", "wijHeq", "qluVok", "dxjxbF"}), expected: []string{"dZwbSR", "wijHeq", "qluVok", "dxjxbF"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
