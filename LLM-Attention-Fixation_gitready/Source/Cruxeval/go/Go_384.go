package f_test

import (
    "testing"
    "fmt"
)

func f(text string, chars string) string {
    var new_text []rune = []rune(text)
    charsMap := make(map[rune]bool)
    for _, char := range chars {
        charsMap[char] = true
    }

    for len(new_text) > 0 && len(text) > 0 {
        if _, ok := charsMap[new_text[0]]; ok {
            new_text = new_text[1:]
        } else {
            break
        }
    }

    return string(new_text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("asfdellos", "Ta"), expected: "sfdellos" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
