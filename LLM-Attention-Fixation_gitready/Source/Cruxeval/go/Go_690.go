package main

import (
    "fmt"
    "strings"
    "strconv"
    "testing"
)

func f(n string) string {
	if strings.Contains(n, ".") {
		num, _ := strconv.ParseFloat(n, 64)
		return strconv.Itoa(int(num) + 3)
	}
	return n
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("800"), expected: "800" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
