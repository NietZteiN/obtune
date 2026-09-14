package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(myString string) string {
	tmp := strings.ToLower(myString)
	for _, char := range strings.ToLower(myString) {
		if strings.Contains(tmp, string(char)) {
			tmp = strings.Replace(tmp, string(char), "", 1)
		}
	}

	return tmp
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("[ Hello ]+ Hello, World!!_ Hi"), expected: "" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
