package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    var letters string
    for i := 0; i < len(text); i++ {
        if text[i] >= 'a' && text[i] <= 'z' || text[i] >= 'A' && text[i] <= 'Z' || text[i] >= '0' && text[i] <= '9' {
            letters += string(text[i])
        }
    }
    return letters
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("we@32r71g72ug94=(823658*!@324"), expected: "we32r71g72ug94823658324" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
