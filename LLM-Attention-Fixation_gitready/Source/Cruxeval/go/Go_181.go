package f_test

import (
    "testing"
    "fmt"
    "unicode"
)

func f(s string) []interface{} {
    count := 0
    digits := ""
    for _, c := range s {
        if unicode.IsDigit(c) {
            count += 1
            digits += string(c)
        }
    }
    return []interface{}{digits, count}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("qwfasgahh329kn12a23"), expected: []interface{}{"3291223", 7} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
