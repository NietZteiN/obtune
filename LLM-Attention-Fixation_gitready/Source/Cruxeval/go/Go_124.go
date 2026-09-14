package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(txt string, sep string, sep_count int) string {
	o := ""
	for sep_count > 0 && strings.Count(txt, sep) > 0 {
		splitTxt := strings.SplitAfterN(txt, sep, 2)
		o += splitTxt[0]
		txt = splitTxt[1]
		sep_count--
	}
	return o + txt
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("i like you", " ", -1), expected: "i like you" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
