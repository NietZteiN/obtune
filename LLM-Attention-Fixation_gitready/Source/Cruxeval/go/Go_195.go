package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	prefixes := []string{"acs", "asp", "scn"}
	for _, p := range prefixes {
		text = strings.TrimPrefix(text, p) + " "
	}
	return strings.TrimPrefix(text, " ")[:len(text)-1]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("ilfdoirwirmtoibsac"), expected: "ilfdoirwirmtoibsac  " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
