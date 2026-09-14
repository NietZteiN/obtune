package f_test

import (
    "fmt"
    "strconv"
    "testing"
)

func f(text string, num_digits int) string {
    width := 1
    if num_digits > 1 {
        width = num_digits
    }
    
    textInt, err := strconv.Atoi(text)
    if err != nil {
        // handle error
        return ""
    }

    return fmt.Sprintf("%0*d", width, textInt)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("19", 5), expected: "00019" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
