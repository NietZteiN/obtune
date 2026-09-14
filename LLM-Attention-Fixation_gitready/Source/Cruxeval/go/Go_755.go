package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(replace string, text string, hide string) string {
    for strings.Contains(text, hide) {
        replace += "ax"
        text = strings.Replace(text, hide, replace, 1)
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
     { actual: candidate("###", "ph>t#A#BiEcDefW#ON#iiNCU", "."), expected: "ph>t#A#BiEcDefW#ON#iiNCU" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
