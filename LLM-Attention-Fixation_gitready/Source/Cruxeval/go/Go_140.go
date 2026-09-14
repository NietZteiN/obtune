package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(st string) string {
	if strings.LastIndex(strings.ToLower(st), "h") >= strings.LastIndex(strings.ToLower(st[:strings.LastIndex(strings.ToLower(st), "i")]), "i") {
		return "Hey"
	} else {
		return "Hi"
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Hi there"), expected: "Hey" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
