package f_test

import (
    "testing"
    "fmt"
)

func f(text string, characters string) string {
    characterList := append([]rune(characters), ' ', '_')

    i := 0
    for i < len(text) {
        found := false
        for _, char := range characterList {
            if rune(text[i]) == char {
                found = true
                break
            }
        }
        if !found {
            break
        }
        i++
    }

    return text[i:]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("2nm_28in", "nm"), expected: "2nm_28in" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
