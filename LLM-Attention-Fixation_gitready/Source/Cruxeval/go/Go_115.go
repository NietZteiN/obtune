package f_test

import (
	"testing"
	"fmt"
)

func f(text string) string {
	res := ""
	for _, ch := range []byte(text) {
		if ch == 61 {
			break
		}
		if ch == 0 {
			continue
		}
		res += fmt.Sprintf("%d; ", ch)
	}
	return fmt.Sprintf("b'%s'", res)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("os||agx5"), expected: "b'111; 115; 124; 124; 97; 103; 120; 53; '" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
