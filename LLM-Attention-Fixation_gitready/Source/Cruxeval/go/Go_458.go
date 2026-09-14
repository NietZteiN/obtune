package f_test

import (
    "testing"
    "fmt"
)

func f(text string, search_chars string, replace_chars string) string {
    transMap := make(map[rune]rune)
    for i, char := range search_chars {
        transMap[char] = rune(replace_chars[i])
    }

    var result string
    for _, char := range text {
        if replace, ok := transMap[char]; ok {
            result += string(replace)
        } else {
            result += string(char)
        }
    }

    return result
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("mmm34mIm", "mm3", ",po"), expected: "pppo4pIp" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
