package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    result := ""
    mid := (len(text) - 1) / 2
    for i := 0; i < mid; i++ {
        result += string(text[i])
    }
    for i := mid; i < len(text)-1; i++ {
        result += string(text[mid + len(text) - 1 - i])
    }
    for len(result) < len(text) {
        result += string(text[len(text)-1])
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
     { actual: candidate("eat!"), expected: "e!t!" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
