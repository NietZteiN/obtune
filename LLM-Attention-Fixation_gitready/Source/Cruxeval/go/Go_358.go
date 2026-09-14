package f_test

import (
    "testing"
    "fmt"
)

func f(text string, value string) string {
    indexes := []int{}
    for i := 0; i < len(text); i++ {
        if string(text[i]) == value && (i == 0 || string(text[i-1]) != value) {
            indexes = append(indexes, i)
        }
    }
    if len(indexes) % 2 == 1 {
        return text
    }
    return text[indexes[0]+1:indexes[len(indexes)-1]]
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("btrburger", "b"), expected: "tr" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
