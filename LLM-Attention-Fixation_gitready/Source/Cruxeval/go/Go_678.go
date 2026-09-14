package f_test

import (
    "testing"
    "fmt"
)

func f(text string) map[string]int {
    freq := make(map[string]int)
    for _, c := range text {
        if c >= 'A' && c <= 'Z' {
            c = c + 32 // convert uppercase to lowercase
        }
        if _, ok := freq[string(c)]; ok {
            freq[string(c)]++
        } else {
            freq[string(c)] = 1
        }
    }
    return freq
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("HI"), expected: map[string]int{"h": 1, "i": 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
