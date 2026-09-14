package f_test

import (
	"strings"
    "testing"
    "fmt"
)

func f(text string) string {
	text = strings.ToLower(text)
	capitalize := strings.ToUpper(string(text[0])) + text[1:]
	return text[:1] + capitalize[1:]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("this And cPanel"), expected: "this and cpanel" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
