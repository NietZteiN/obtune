package f_test

import (
    "testing"
    "fmt"
)

func f(text string, m int, n int) string {
    text = text + text[:m] + text[n:]
    result := ""
    for i := n; i < len(text)-m; i++ {
        result = string(text[i]) + result
    }
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("abcdefgabc", 1, 2), expected: "bagfedcacbagfedc" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
