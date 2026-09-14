package f_test

import (
    "strings"
    "testing"
    "fmt"
)

func f(text string) string {
    l := strings.LastIndex(text, "0")
    if l == -1 {
        return "-1:-1"
    }
    return fmt.Sprintf("%d:%d", l, strings.Index(text[l+1:], "0") + 1)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("qq0tt"), expected: "2:0" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
