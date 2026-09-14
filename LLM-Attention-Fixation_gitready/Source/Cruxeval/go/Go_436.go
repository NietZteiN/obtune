package f_test

import (
    "testing"
    "fmt"
)

func f(s string, characters []int) []string {
    var result []string
    for _, i := range characters {
        result = append(result, s[i:i+1])
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
     { actual: candidate("s7 6s 1ss", []int{1, 3, 6, 1, 2}), expected: []string{"7", "6", "1", "7", " "} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
