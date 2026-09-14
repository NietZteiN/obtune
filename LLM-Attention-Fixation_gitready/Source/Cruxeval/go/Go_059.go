package f_test

import (
    "testing"
    "fmt"
)

func f(s string) string {
    a := make([]rune, 0)
    for _, char := range s {
        if char != ' ' {
            a = append(a, char)
        }
    }
    b := a
    for i := len(a) - 1; i >= 0; i-- {
        if a[i] == ' ' {
            b = b[:len(b)-1]
        } else {
            break
        }
    }
    return string(b)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("hi "), expected: "hi" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
