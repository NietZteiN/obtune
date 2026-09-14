package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    var result []rune
    for _, char := range text {
        if char > 127 {
            return ""
        } else if (char >= 'a' && char <= 'z') || (char >= 'A' && char <= 'Z') {
            result = append(result, char-32)
        } else {
            result = append(result, char)
        }
    }
    return string(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("ua6hajq"), expected: "UA6HAJQ" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
