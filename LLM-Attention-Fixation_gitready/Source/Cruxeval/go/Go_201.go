package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    var chars []byte
    for _, c := range text {
        if c >= '0' && c <= '9' {
            chars = append(chars, byte(c))
        }
    }
    // Reverse the chars slice
    for i, j := 0, len(chars)-1; i < j; i, j = i+1, j-1 {
        chars[i], chars[j] = chars[j], chars[i]
    }
    return string(chars)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("--4yrw 251-//4 6p"), expected: "641524" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
