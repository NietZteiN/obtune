package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(input_string string) string {
    for strings.Contains(input_string, "a") || strings.Contains(input_string, "A") {
        input_string = strings.NewReplacer("a", "i", "A", "i").Replace(input_string)
    }
    return input_string
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("biec"), expected: "biec" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
