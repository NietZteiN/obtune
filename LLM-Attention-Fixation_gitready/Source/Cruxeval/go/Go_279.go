package main

import (
    "fmt"
    "strings"
    "testing"
)

func partition(s, sep string) (string, string, string) {
	idx := strings.Index(s, sep)
	if idx == -1 {
		return s, "", ""
	}
	return s[:idx], sep, s[idx+len(sep):]
}

func f(text string) string {
	ans := ""
	for text != "" {
		x, sep, remaining := partition(text, "(")
		ans = x + strings.ReplaceAll(sep, "(", "|") + ans
		ans = ans + string(remaining[0]) + ans
		text = remaining[1:]
	}
	return ans
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(""), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
