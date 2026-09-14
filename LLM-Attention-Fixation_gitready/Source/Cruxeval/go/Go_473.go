package f_test

import (
    "testing"
    "fmt"
)

func f(text string, value string) string {
    indexes := []int{}
    for i := 0; i < len(text); i++ {
        if string(text[i]) == value {
            indexes = append(indexes, i)
        }
    }
    new_text := []rune(text)
    for i := len(indexes) - 1; i >= 0; i-- {
        new_text = append(new_text[:indexes[i]], new_text[indexes[i]+1:]...)
    }
    return string(new_text)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("scedvtvotkwqfoqn", "o"), expected: "scedvtvtkwqfqn" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
