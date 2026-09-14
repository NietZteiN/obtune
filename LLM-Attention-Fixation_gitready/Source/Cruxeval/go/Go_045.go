package f_test

import (
    "testing"
    "fmt"
)

func f(text string, letter string) int {
    counts := make(map[string]int)
    for _, char := range text {
        if _, ok := counts[string(char)]; !ok {
            counts[string(char)] = 1
        } else {
            counts[string(char)]++
        }
    }
    return counts[letter]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("za1fd1as8f7afasdfam97adfa", "7"), expected: 2 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
