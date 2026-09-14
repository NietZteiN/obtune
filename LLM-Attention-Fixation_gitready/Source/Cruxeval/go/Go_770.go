package f_test

import (
	"strings"
	"testing"
	"fmt"
)

func f(line string, char string) string {
	count := strings.Count(line, char)
	for i := count + 1; i > 0; i-- {
		line = center(line, len(line)+i/len(char), char)
	}
	return line
}

func center(input string, length int, filler string) string {
	lpad := (length - len(input)) / 2
	rpad := length - (len(input) + lpad)
	return strings.Repeat(filler, lpad) + input + strings.Repeat(filler, rpad)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("$78", "$"), expected: "$$78$$" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
