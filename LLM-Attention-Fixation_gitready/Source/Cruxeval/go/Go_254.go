package f_test

import (
    "strings"
    "testing"
    "fmt"
)

func f(text string, repl string) string {
    trans := make(map[rune]rune)
    for i, char := range strings.ToLower(text) {
        if i < len(repl) {
            trans[char] = rune(repl[i])
        } else {
            trans[char] = char
        }
    }
    result := make([]rune, len(text))
    for i, char := range strings.ToLower(text) {
        if val, ok := trans[char]; ok {
            result[i] = val
        } else {
            result[i] = char
        }
    }
    return string(result)
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("upper case", "lower case"), expected: "lwwer case" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
