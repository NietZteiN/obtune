package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    var a []rune
    for _, char := range text {
        if char < '0' || char > '9' {
            a = append(a, char)
        }
    }
    return string(a)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("seiq7229 d27"), expected: "seiq d" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
