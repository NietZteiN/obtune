package f_test

import (
    "strings"
    "testing"
    "fmt"
)

func f(text string) string {
    ls := []rune(text)
    for i, j := 0, len(ls)-1; i < j; i, j = i+1, j-1 {
        ls[i], ls[j] = ls[j], ls[i]
    }
    text2 := ""
    for i := len(ls) - 3; i > 0; i -= 3 {
        text2 += strings.Join([]string{string(ls[i]), string(ls[i+1]), string(ls[i+2])}, "---") + "---"
    }
    return text2[:len(text2)-3]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("scala"), expected: "a---c---s" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
