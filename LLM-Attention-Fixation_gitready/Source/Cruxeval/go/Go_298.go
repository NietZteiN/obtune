package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    new_text := []rune(text)
    for i := 0; i < len(new_text); i++ {
        character := new_text[i]
        new_character := string(character)
        if character >= 'a' && character <= 'z' {
            new_character = string(character - 32)
        } else if character >= 'A' && character <= 'Z' {
            new_character = string(character + 32)
        }
        new_text[i] = []rune(new_character)[0]
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
     { actual: candidate("dst vavf n dmv dfvm gamcu dgcvb."), expected: "DST VAVF N DMV DFVM GAMCU DGCVB." },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
