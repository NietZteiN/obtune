package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string, c1 string, c2 string) string {
	if s == "" {
		return s
	}

	ls := strings.Split(s, c1)
	for index, item := range ls {
		if strings.Contains(item, c1) {
			ls[index] = strings.Replace(item, c1, c2, 1)
		}
	}
	return strings.Join(ls, c1)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("", "mi", "siast"), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
