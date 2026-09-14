package f_test

import (
    "testing"
    "fmt"
)

func f(items []string) []string {
    var result []string
    for _, item := range items {
        for _, d := range item {
            if d < '0' || d > '9' {
                result = append(result, string(d))
            }
        }
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
     { actual: candidate([]string{"123", "cat", "d dee"}), expected: []string{"c", "a", "t", "d", " ", "d", "e", "e"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
