package f_test

import (
    "testing"
    "fmt"
)

func f(myString string) int {
    upper := 0
    for _, c := range myString {
        if c >= 'A' && c <= 'Z' {
            upper++
        }
    }
    return upper * [2]int{2, 1}[upper%2]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("PoIOarTvpoead"), expected: 8 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
