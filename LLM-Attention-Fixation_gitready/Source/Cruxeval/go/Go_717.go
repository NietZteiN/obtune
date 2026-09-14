package f_test

import (
    "fmt"
    "testing"
)

func isLetter(c byte) bool {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
}

func f(text string) string {
    k, l := 0, len(text)-1
    for !isLetter(text[l]) {
        l--
    }
    for !isLetter(text[k]) {
        k++
    }
    if k != 0 || l != len(text)-1 {
        return text[k : l+1]
    } else {
        return string(text[0])
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("timetable, 2mil"), expected: "t" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
