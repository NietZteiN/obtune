package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    i := (len(text) + 1) / 2
    result := []byte(text)
    for i < len(text) {
        t := result[i]
        if t >= 'A' && t <= 'Z' {
            result[i] = t + 32
        }
        i += 2
    }
    return string(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("mJkLbn"), expected: "mJklbn" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
