package f_test

import (
    "testing"
    "fmt"
)

func f(w string) bool {
    ls := []rune(w)
    omw := ""
    for len(ls) > 0 {
        omw += string(ls[0])
        ls = ls[1:]
        if len(ls)*2 > len(w) {
            return w[len(ls):] == omw
        }
    }
    return false
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("flak"), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
