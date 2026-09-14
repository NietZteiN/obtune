package f_test

import (
    "testing"
    "fmt"
)

func f(text string, count int) string {
    for i := 0; i < count; i++ {
        var reversed string
        for _, char := range text {
            reversed = string(char) + reversed
        }
        text = reversed
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
     { actual: candidate("439m2670hlsw", 3), expected: "wslh0762m934" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
