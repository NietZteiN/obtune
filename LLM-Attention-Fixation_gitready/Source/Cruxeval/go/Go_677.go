package f_test

import (
	"testing"
	"fmt"
)

func f(text string, length int) string {
	if length < 0 {
		length = -length
	}
	output := ""
	for idx := 0; idx < length; idx++ {
		if text[idx%len(text)] != ' ' {
			output += string(text[idx%len(text)])
		} else {
			break
		}
	}
	return output
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("I got 1 and 0.", 5), expected: "I" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
