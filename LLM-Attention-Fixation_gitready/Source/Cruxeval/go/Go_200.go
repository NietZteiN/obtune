package f_test

import (
    "testing"
    "fmt"
)

func f(text string, value string) string {
    length := len(text)
    index := 0
    for length > 0 {
        value = string(text[index]) + value
        length--
        index++
    }
    return value
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("jao mt", "house"), expected: "tm oajhouse" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
