package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(a string, split_on string) bool {
	t := strings.Split(a, " ")
	var runes []rune
	for _, i := range t {
		for _, j := range i {
			runes = append(runes, j)
		}
	}
	if strings.ContainsRune(string(runes), rune(split_on[0])) {
		return true
	} else {
		return false
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("booty boot-boot bootclass", "k"), expected: false },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
