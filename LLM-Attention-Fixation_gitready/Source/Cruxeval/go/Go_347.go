package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    ls := []rune(text)
    length := len(ls)
    for i := 0; i < length; i++ {
        ls = append(ls[:i], append([]rune{ls[i]}, ls[i:]...)...)
    }
    result := string(ls)
    for len(result) < length*2 {
        result += " "
    }
    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("hzcw"), expected: "hhhhhzcw" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
