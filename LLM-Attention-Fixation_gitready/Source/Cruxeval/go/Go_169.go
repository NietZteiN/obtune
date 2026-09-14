package f_test

import (
	"testing"
	"fmt"
)

func f(text string) string {
	ls := []rune(text)
	total := (len(text) - 1) * 2
	for i := 1; i <= total; i++ {
		if i%2 == 1 {
			ls = append(ls, '+')
		} else {
			ls = append([]rune{'+'}, ls...)
		}
	}
	return fmt.Sprintf("%*s", total, string(ls))
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("taole"), expected: "++++taole++++" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
