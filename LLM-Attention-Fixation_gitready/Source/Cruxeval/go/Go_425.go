package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(a string) []string {
    a = strings.ReplaceAll(a, "/", ":")
    z := strings.SplitN(a, ":", 2)
    if len(z) == 1 {
        return []string{"", "", z[0]}
    }
    return []string{z[0], ":", z[1]}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("/CL44     "), expected: []string{"", ":", "CL44     "} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
