package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    if text == "" {
        return "non ascii"
    }

    for _, c := range text {
        if c > 127 {
            return "non ascii"
        }
    }
    
    return "ascii"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("<<<<"), expected: "ascii" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
