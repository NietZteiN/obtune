package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(url string) string {
    return strings.TrimPrefix(url, "http://www.")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("https://www.www.ekapusta.com/image/url"), expected: "https://www.www.ekapusta.com/image/url" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
