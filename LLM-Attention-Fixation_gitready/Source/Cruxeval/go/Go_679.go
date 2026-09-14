package f_test

import (
    "testing"
    "fmt"
)

func f(text string) bool {
    if text == "" {
        return false
    }
    firstChar := text[0]
    if firstChar >= '0' && firstChar <= '9' {
        return false
    }
    for _, lastChar := range text {
        if lastChar != '_' && (lastChar < 'A' || lastChar > 'Z') && (lastChar < 'a' || lastChar > 'z') && (lastChar < '0' || lastChar > '9') {
            return false
        }
    }
    return true
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("meet"), expected: true },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
