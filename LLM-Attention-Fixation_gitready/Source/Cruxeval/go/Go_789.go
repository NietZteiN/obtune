package f_test

import (
    "testing"
    "fmt"
)

func f(text string, n int) string {
    if n < 0 || len(text) <= n {
        return text
    }
    result := text[0:n]
    i := len(result) - 1
    for i >= 0 {
        if result[i] != text[i] {
            break
        }
        i--
    }
    return text[0 : i+1]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("bR", -1), expected: "bR" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
