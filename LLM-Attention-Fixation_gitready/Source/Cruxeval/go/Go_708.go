package f_test

import (
    "testing"
    "fmt"
)

func f(myString string) string {
    l := []rune(myString)
    for i := len(l) - 1; i >= 0; i-- {
        if l[i] != ' ' {
            break
        }
        l = append(l[:i], l[i+1:]...)
    }
    return string(l)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("    jcmfxv     "), expected: "    jcmfxv" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
