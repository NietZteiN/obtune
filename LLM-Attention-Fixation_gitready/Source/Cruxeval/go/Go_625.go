package f_test

import (
    "testing"
    "fmt"
)

func f(text string) int {
    count := 0
    for _, i := range text {
        if i == '.' || i == '?' || i == '!' || i == ',' {
            count++
        }
    }
    return count
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("bwiajegrwjd??djoda,?"), expected: 4 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
