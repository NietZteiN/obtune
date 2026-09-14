package f_test

import (
    "testing"
    "fmt"
)

func f(r string, w string) []string {
    a := make([]string, 0)
    if r[0] == w[0] && w[len(w)-1] == r[len(r)-1] {
        a = append(a, r)
        a = append(a, w)
    } else {
        a = append(a, w)
        a = append(a, r)
    }
    return a
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("ab", "xy"), expected: []string{"xy", "ab"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
