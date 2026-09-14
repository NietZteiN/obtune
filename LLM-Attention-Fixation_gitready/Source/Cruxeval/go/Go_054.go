package f_test

import (
    "testing"
    "fmt"
)

func f(text string, s int, e int) int {
    sublist := text[s:e]
    if sublist == "" {
        return -1
    }
    minIndex := 0
    for i, c := range sublist {
        if c < rune(sublist[minIndex]) {
            minIndex = i
        }
    }
    return minIndex
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("happy", 0, 3), expected: 1 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
