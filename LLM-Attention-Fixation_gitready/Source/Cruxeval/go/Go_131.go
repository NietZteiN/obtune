package f_test

import (
    "strings"
    "testing"
    "fmt"
)

func f(text string) int {
    a := len(text)
    count := 0
    for len(text) > 0 {
        if strings.HasPrefix(text, "a") {
            count += strings.Index(text, " ")
        } else {
            count += strings.Index(text, "\n")
        }
        newStart := strings.Index(text, "\n") + 1
        if newStart < 0 {
            break
        }
        newEnd := newStart + a + 1
        if newEnd >= len(text) {
            newEnd = len(text)
        }
        text = text[newStart:newEnd]
    }
    return count
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("a\nkgf\nasd\n"), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
