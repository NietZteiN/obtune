package f_test

import (
    "testing"
    "fmt"
)

func f(char_map map[string]string, text string) string {
    new_text := ""
    for _, ch := range text {
        val, ok := char_map[string(ch)]
        if !ok {
            new_text += string(ch)
        } else {
            new_text += val
        }
    }
    return new_text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]string{}, "hbd"), expected: "hbd" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
