package f_test

import (
    "testing"
    "fmt"
)

func f(text string) []string {
    var new_text []string
    for i := 0; i < len(text)/3; i++ {
        new_text = append(new_text, fmt.Sprintf("< %s level=%d >", text[i*3:i*3+3], i))
    }
    lastItem := text[len(text)/3*3:]
    new_text = append(new_text, fmt.Sprintf("< %s level=%d >", lastItem, len(text)/3))
    return new_text
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("C7"), expected: []string{"< C7 level=0 >"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
