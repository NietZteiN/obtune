package f_test

import (
    "testing"
    "fmt"
)

func f(text string, insert string) string {
    whitespaces := map[rune]bool{'\t': true, '\r': true, '\v': true, ' ': true, '\f': true, '\n': true}
    var clean string
    for _, char := range text {
        if whitespaces[char] {
            clean += insert
        } else {
            clean += string(char)
        }
    }
    return clean
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("pi wa", "chi"), expected: "pichiwa" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
