package f_test

import (
    "testing"
    "fmt"
)

func f(text string, fill string, size int) string {
    if size < 0 {
        size = -size
    }
    if len(text) > size {
        return text[len(text)-size:]
    }
    return fmt.Sprintf("%"+string(fill)+"*s", size, text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("no asw", "j", 1), expected: "w" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
