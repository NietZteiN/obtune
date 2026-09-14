package f_test

import (
    "testing"
    "fmt"
)

func f(text string, char1 string, char2 string) string {
    t1a := make([]rune, len(char1))
    t2a := make([]rune, len(char2))
    for i, char := range char1 {
        t1a[i] = char
        t2a[i] = []rune(char2)[i]
    }

    t1 := make(map[rune]rune)
    for i := 0; i < len(t1a); i++ {
        t1[t1a[i]] = t2a[i]
    }

    result := ""
    for _, char := range text {
        mappedChar, ok := t1[char]
        if ok {
            result += string(mappedChar)
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
     { actual: candidate("ewriyat emf rwto segya", "tey", "dgo"), expected: "gwrioad gmf rwdo sggoa" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
