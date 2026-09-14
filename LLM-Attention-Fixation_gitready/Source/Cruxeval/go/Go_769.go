package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    textList := []rune(text)
    for i, char := range textList {
        if char >= 'a' && char <= 'z' {
            textList[i] = char - 32
        } else if char >= 'A' && char <= 'Z' {
            textList[i] = char + 32
        }
    }
    return string(textList)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("akA?riu"), expected: "AKa?RIU" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
