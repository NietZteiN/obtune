package f_test

import (
    "fmt"
    "strings"
    "testing"
)

func f(text string, chars string) string {
    listchars := []rune(chars)
    for i := 0; i < len(listchars)-1; i++ {
        index := strings.Index(text, string(listchars[i]))
        text = text[:index] + string(listchars[i]) + text[index+1:]
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
     { actual: candidate("tflb omn rtt", "m"), expected: "tflb omn rtt" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
