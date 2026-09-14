package f_test

import (
    "testing"
    "fmt"
)

func f(text string, suffix string) string {
    output := text
    for len(output) >= len(suffix) && output[len(output)-len(suffix):] == suffix {
        output = output[:len(output)-len(suffix)]
    }
    return output
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("!klcd!ma:ri", "!"), expected: "!klcd!ma:ri" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
