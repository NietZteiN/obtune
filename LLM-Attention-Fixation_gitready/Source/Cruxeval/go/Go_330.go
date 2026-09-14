package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    var ans []rune
    for _, char := range text {
        if char >= '0' && char <= '9' {
            ans = append(ans, char)
        } else {
            ans = append(ans, ' ')
        }
    }
    return string(ans)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("m4n2o"), expected: " 4 2 " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
