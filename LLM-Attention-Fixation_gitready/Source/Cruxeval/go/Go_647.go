package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(text string, chunks int) []string {
    return strings.Split(text, "\n")
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("/alcm@ an)t//eprw)/e!/d\nujv", 0), expected: []string{"/alcm@ an)t//eprw)/e!/d", "ujv"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
