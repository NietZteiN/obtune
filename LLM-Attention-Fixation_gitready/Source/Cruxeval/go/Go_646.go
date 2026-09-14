package f_test

import (
    "testing"
    "fmt"
)

func f(text string, count int) string {
    for i := 0; i < count; i++ {
        var reversedText string
        for _, char := range text {
            reversedText = string(char) + reversedText
        }
        text = reversedText
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
     { actual: candidate("aBc, ,SzY", 2), expected: "aBc, ,SzY" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
