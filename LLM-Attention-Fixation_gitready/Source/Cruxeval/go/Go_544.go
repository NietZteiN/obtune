package main

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string) string {
    a := strings.Split(text, "\n")
    var b []string
    for i := 0; i < len(a); i++ {
        c := strings.ReplaceAll(a[i], "\t", "    ")
        b = append(b, c)
    }
    return strings.Join(b, "\n")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("			tab tab tabulates"), expected: "            tab tab tabulates" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
