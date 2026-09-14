package f_test

import (
    "testing"
    "fmt"
)

func f(s string) []string {
    d := make(map[rune]bool)
    for _, char := range s {
        d[char] = true
    }

    result := []string{}
    for key := range d {
        result = append(result, string(key))
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
     { actual: candidate("12ab23xy"), expected: []string{"1", "2", "a", "b", "3", "x", "y"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
