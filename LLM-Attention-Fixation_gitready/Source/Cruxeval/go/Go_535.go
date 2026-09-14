package f_test

import (
    "testing"
    "fmt"
)

func f(n int) bool {
    for _, c := range fmt.Sprint(n) {
        if c != '0' && c != '1' && c != '2' && (c < '5' || c > '9') {
            return false
        }
    }
    return true
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(1341240312), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
