package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(n string, s string) string {
    if strings.HasPrefix(s, n) {
        pre := strings.Split(s, n)[0]
        return pre + n + s[len(n):]
    }
    return s
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("xqc", "mRcwVqXsRDRb"), expected: "mRcwVqXsRDRb" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
