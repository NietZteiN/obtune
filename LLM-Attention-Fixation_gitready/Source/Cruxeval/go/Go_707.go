package f_test

import (
    "testing"
    "fmt"
)

func f(text string, position int) string {
    length := len(text)
    index := position % (length + 1)
    if position < 0 || index < 0 {
        index = -1
    }
    new_text := []rune(text)
    new_text = append(new_text[:index], new_text[index+1:]...)
    return string(new_text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("undbs l", 1), expected: "udbs l" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
