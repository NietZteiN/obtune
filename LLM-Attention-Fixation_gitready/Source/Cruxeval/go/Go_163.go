package f_test

import (
    "testing"
    "fmt"
)

func f(text string, space_symbol string, size int) string {
    spaces := ""
    for i := 0; i < size-len(text); i++ {
        spaces += space_symbol
    }
    return text + spaces
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("w", "))", 7), expected: "w))))))))))))" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
