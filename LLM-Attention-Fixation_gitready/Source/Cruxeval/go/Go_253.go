package f_test

import (
    "testing"
    "fmt"
)

func f(text string, pref string) string {
    length := len(pref)
    if pref == text[:length] {
        return text[length:]
    }
    return text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("kumwwfv", "k"), expected: "umwwfv" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
