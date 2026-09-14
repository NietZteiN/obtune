package f_test

import (
    "testing"
    "fmt"
)

func f(text string, function string) []int {
    cites := []int{len(text[len(function):])}
    for _, char := range text {
        if string(char) == function {
            cites = append(cites, len(text[len(function):]))
        }
    }
    return cites
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("010100", "010"), expected: []int{3} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
