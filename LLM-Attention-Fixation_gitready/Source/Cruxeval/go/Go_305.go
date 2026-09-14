package f_test

import (
    "testing"
    "fmt"
)

func f(text string, char string) string {
    length := len(text)
    index := -1
    for i := 0; i < length; i++ {
        if string(text[i]) == char {
            index = i
        }
    }
    if index == -1 {
        index = length / 2
    }
    new_text := []rune(text)
    new_text = append(new_text[:index], new_text[index+1:]...)
    return string(new_text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("o horseto", "r"), expected: "o hoseto" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
