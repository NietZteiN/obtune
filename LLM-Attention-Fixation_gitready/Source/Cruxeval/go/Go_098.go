package f_test

import (
    "testing"
    "fmt"
    "strings"
    "unicode"
)

func f(s string) int {
    count := 0
    for _, word := range strings.Fields(s) {
        for i, r := range word {
            if unicode.IsUpper(r) != (i == 0) {
                count -= 1
                break
            }
        }
        count += 1
    }
    return count
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("SOME OF THIS Is uknowN!"), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
