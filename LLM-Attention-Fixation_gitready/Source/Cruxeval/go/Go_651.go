package f_test

import (
	"strings"
	"testing"
	"unicode"
	"fmt"
)

func f(text, letter string) string {
	if unicode.IsLower(rune(letter[0])) {
		letter = strings.ToUpper(letter)
	}
	var result []rune
	for _, c := range text {
		if rune(unicode.ToLower(c)) == rune(letter[0]) {
			result = append(result, rune(letter[0]))
		} else {
			result = append(result, c)
		}
	}
	result[0] = unicode.ToUpper(result[0])
	return string(result)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("E wrestled evil until upperfeat", "e"), expected: "E wrestled evil until upperfeat" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
