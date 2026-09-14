package f_test

import (
    "testing"
    "fmt"
)

func f(text string, n int) string {
    if len(text) <= 2 {
        return text
    }
    leadingChars := ""
    for i := 0; i < n-len(text)+1; i++ {
        leadingChars += string(text[0])
    }
    return leadingChars + text[1:len(text)-1] + string(text[len(text)-1])
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("g", 15), expected: "g" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
