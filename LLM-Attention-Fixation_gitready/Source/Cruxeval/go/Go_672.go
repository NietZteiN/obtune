package f_test

import (
    "testing"
    "fmt"
)

func f(text string, position int, value string) string {
    length := len(text)
    index := (position % (length + 2)) - 1
    if index >= length || index < 0 {
        return text
    }
    textList := []rune(text)
    textList[index] = []rune(value)[0]
    return string(textList)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("1zd", 0, "m"), expected: "1zd" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
