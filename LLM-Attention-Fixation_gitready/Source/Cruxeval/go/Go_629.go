package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, dng string) string {
    if idx := strings.Index(text, dng); idx == -1 {
        return text
    } else if text[idx:] == dng {
        return text[:idx]
    } else {
        return text[:idx] + f(text[:idx-1], dng)
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("catNG", "NG"), expected: "cat" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
