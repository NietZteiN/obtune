package f_test

import (
    "testing"
    "fmt"
)

func f(txt string) string {
    var d []rune
    for _, c := range txt {
        if c >= '0' && c <= '9' {
            continue
        }
        if c >= 'a' && c <= 'z' {
            d = append(d, c-32)
        } else if c >= 'A' && c <= 'Z' {
            d = append(d, c+32)
        }
    }
    return string(d)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("5ll6"), expected: "LL" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
