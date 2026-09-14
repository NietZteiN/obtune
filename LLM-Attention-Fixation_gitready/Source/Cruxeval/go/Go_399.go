package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, old string, new string) string {
    if len(old) > 3 {
        return text
    }
    if strings.Contains(text, old) && !strings.Contains(text, " ") {
        return strings.ReplaceAll(text, old, strings.Repeat(new, len(old)))
    }
    for strings.Contains(text, old) {
        text = strings.ReplaceAll(text, old, new)
    }
    return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("avacado", "va", "-"), expected: "a--cado" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
