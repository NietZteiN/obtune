package f_test

import (
    "testing"
    "fmt"
)

func f(text string) []string {
    text_arr := make([]string, 0)
    for j := 0; j < len(text); j++ {
        text_arr = append(text_arr, text[j:])
    }
    return text_arr
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("123"), expected: []string{"123", "23", "3"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
