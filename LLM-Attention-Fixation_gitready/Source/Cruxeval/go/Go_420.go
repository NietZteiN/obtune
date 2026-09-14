package f_test

import (
    "testing"
    "fmt"
)

func f(text string) bool {
    if text == "" {
        return false
    }
    
    for _, char := range text {
        if (char < 'a' || char > 'z') && (char < 'A' || char > 'Z') {
            return false
        }
    }
    
    return true
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("x"), expected: true },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
