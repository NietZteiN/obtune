package f_test

import (
    "testing"
    "fmt"
)

func f(text string, amount int) string {
    length := len(text)
    preText := "|"
    if amount >= length {
        extraSpace := amount - length
        for i := 0; i < extraSpace/2; i++ {
            preText += " "
        }
        return preText + text + preText
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
     { actual: candidate("GENERAL NAGOOR", 5), expected: "GENERAL NAGOOR" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
