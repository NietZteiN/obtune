package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    count := len(text)
    for i := -count + 1; i < 0; i++ {
        text = text + string(text[len(text)+i])
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
     { actual: candidate("wlace A"), expected: "wlace Alc l  " },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
