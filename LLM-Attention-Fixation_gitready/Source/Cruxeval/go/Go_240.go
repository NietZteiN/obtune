package f_test

import (
    "testing"
    "fmt"
    "strings"
    "strconv"
)

func f(float_number float64) string {
    number := strconv.FormatFloat(float_number, 'f', -1, 64)
    dot := strings.Index(number, ".")
    if dot != -1 {
        if len(number[dot+1:]) < 2 {
            return number[:dot] + "." + string(number[dot+1:]) + strings.Repeat("0", 2-len(number[dot+1:]))
        }
        return number[:dot] + "." + string(number[dot+1:])
    }
    return number + ".00"
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(3.121), expected: "3.121" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
