package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    var short string
    for _, c := range text {
        if c >= 'a' && c <= 'z' {
            short += string(c)
        }
    }
    return short
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("980jio80jic kld094398IIl "), expected: "jiojickldl" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
