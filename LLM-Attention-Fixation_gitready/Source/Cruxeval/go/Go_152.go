package f_test

import (
    "testing"
    "fmt"
    "unicode"
)

func f(text string) int {
    n := 0
    for _, char := range text {
        if unicode.IsUpper(char) {
            n++
        }
    }
    return n
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("AAAAAAAAAAAAAAAAAAAA"), expected: 20 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
