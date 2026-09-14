package f_test

import (
    "testing"
    "fmt"
    "unicode"
)

func f(st string) string {
    swapped := ""
    for _, ch := range st {
        if unicode.IsUpper(ch) {
            swapped = string(unicode.ToLower(ch)) + swapped
        } else {
            swapped = string(unicode.ToUpper(ch)) + swapped
        }
    }
    return swapped
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("RTiGM"), expected: "mgItr" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
