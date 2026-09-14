package f_test

import (
    "testing"
    "fmt"
)

func f(total []string, arg string) []string {
    for _, e := range arg {
        total = append(total, string(e))
    }
    return total
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"1", "2", "3"}, "nammo"), expected: []string{"1", "2", "3", "n", "a", "m", "m", "o"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
