package f_test

import (
    "testing"
    "fmt"
)

func f(n int) string {
    t := 0
    b := ""
    digits := []int{}
    numStr := fmt.Sprint(n)
    for _, char := range numStr {
        digit := int(char - '0')
        digits = append(digits, digit)
    }

    for _, d := range digits {
        if d == 0 {
            t++
        } else {
            break
        }
    }

    for i := 0; i < t; i++ {
        b += "10" + "4"
    }
    b += fmt.Sprint(n)
    return b
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(372359), expected: "372359" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
