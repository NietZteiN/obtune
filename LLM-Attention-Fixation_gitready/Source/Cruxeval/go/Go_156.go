package f_test

import (
    "testing"
    "fmt"
)

func f(text string, limit int, char string) string {
    if limit < len(text) {
        return text[:limit]
    }
    return fmt.Sprintf("%-[1]*[2]s", limit, text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("tqzym", 5, "c"), expected: "tqzym" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
