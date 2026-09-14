package f_test

import (
    "testing"
    "fmt"
)

func f(text string) bool {
    b := true
    for _, x := range text {
        if x >= '0' && x <= '9' {
            b = true
        } else {
            b = false
            break
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
     { actual: candidate("-1-3"), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
