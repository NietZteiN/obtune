package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(s string) string {
    return strings.ToUpper(s)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("Jaafodsfa SOdofj AoaFjIs  JAFasIdfSa1"), expected: "JAAFODSFA SODOFJ AOAFJIS  JAFASIDFSA1" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
