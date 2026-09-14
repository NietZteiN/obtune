package f_test

import (
    "testing"
    "fmt"
)

func f(text string) int {
    result_list := []string{"3", "3", "3", "3"}
    if len(result_list) > 0 {
        result_list = nil
    }
    return len(text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("mrq7y"), expected: 5 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
