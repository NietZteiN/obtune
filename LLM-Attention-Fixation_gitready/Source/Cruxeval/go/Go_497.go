package f_test

import (
    "testing"
    "fmt"
)

func f(n int) []string {
    b := []string{}
    strN := fmt.Sprint(n)
    for i := 0; i < len(strN); i++ {
        b = append(b, string(strN[i]))
        if i >= 2 {
            b[i] += "+"
        }
    }
    return b
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(44), expected: []string{"4", "4"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
