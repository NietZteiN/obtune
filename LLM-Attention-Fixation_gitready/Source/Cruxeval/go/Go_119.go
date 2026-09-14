package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    var result string
    for i := 0; i < len(text); i++ {
        if i % 2 == 0 {
            result += string(text[i] ^ 32)
        } else {
            result += string(text[i])
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
     { actual: candidate("vsnlygltaw"), expected: "VsNlYgLtAw" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
