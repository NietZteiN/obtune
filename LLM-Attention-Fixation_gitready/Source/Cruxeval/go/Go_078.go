package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
	if text != "" && strings.ToUpper(text) == text {
		cs := strings.NewReplacer(
			"A", "a",
			"B", "b",
			"C", "c",
			"D", "d",
			"E", "e",
			"F", "f",
			"G", "g",
			"H", "h",
			"I", "i",
			"J", "j",
			"K", "k",
			"L", "l",
			"M", "m",
			"N", "n",
			"O", "o",
			"P", "p",
			"Q", "q",
			"R", "r",
			"S", "s",
			"T", "t",
			"U", "u",
			"V", "v",
			"W", "w",
			"X", "x",
			"Y", "y",
			"Z", "z",
		)
		return cs.Replace(text)
	}
	return strings.ToLower(text)[:3]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("mTYWLMwbLRVOqNEf.oLsYkZORKE[Ko[{n"), expected: "mty" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
