package f_test

import (
    "testing"
    "fmt"
    "unicode"
)

func f(s string) string {
    result := ""
    for _, c := range s {
        if unicode.IsSpace(c) {
            result += string(c)
        }
    }
    return result
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("\ngiyixjkvu\n rgjuo"), expected: "\n\n " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
