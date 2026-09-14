package f_test

import (
    "testing"
    "fmt"
)

func f(text string, value string) string {
    textList := []rune(text)
    textList = append(textList, []rune(value)...)
    return string(textList)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("bcksrut", "q"), expected: "bcksrutq" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
