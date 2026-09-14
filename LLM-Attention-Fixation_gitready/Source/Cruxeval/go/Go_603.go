package main

import (
    "fmt"
    "strings"
    "strconv"
    "testing"
)

func f(sentences string) string {
	splitSentences := strings.Split(sentences, ".")
	oscillating := true
	for _, sentence := range splitSentences {
		if _, err := strconv.Atoi(sentence); err != nil {
			oscillating = false
			break
		}
	}
	if oscillating {
		return "oscillating"
	} else {
		return "not oscillating"
	}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("not numbers"), expected: "not oscillating" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
