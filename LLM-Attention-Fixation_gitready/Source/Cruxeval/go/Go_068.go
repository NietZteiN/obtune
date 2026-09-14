package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, pref string) string {
	if strings.HasPrefix(text, pref) {
		n := len(pref)
		parts := strings.Split(text[n:], ".")[1:]
		parts = append(parts, strings.Split(text[:n], ".")[:len(strings.Split(text[:n], "."))-1]...)
		text = strings.Join(parts, ".")
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
     { actual: candidate("omeunhwpvr.dq", "omeunh"), expected: "dq" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
