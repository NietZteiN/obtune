package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    if text == "identifier" {
        var result string
        for _, c := range text {
            if c >= '0' && c <= '9' {
                result += string(c)
            }
        }
        return result
    } else {
        return text
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("816"), expected: "816" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
