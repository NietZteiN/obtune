package f_test

import (
    "testing"
    "fmt"
    "strings"
)

func f(num string) string {
    letter := 1
    for i := '1'; i <= '9' ; i++ {
        num = strings.Replace(num, string(i), "", -1)
        if len(num) == 0 {
            break
        }
        if letter < len(num) {
            num = num[letter:] + num[:letter]
        }
        letter += 1
    }
    return num
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("bwmm7h"), expected: "mhbwm" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
