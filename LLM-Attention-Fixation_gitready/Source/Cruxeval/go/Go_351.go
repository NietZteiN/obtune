package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	for {
		if !strings.Contains(text, "nnet lloP") {
			break
		}
		text = strings.Replace(text, "nnet lloP", "nnet loLp", -1)
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
     { actual: candidate("a_A_b_B3 "), expected: "a_A_b_B3 " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
