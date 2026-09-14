package f_test

import (
    "testing"
    "fmt"
)

func f(names []string, winners []string) []int {
    var ls []int
    for _, winner := range winners {
        for i := 0; i < len(names); i++ {
            if names[i] == winner {
                ls = append(ls, i)
            }
        }
    }

    // Sorting in descending order
    for i := 0; i < len(ls); i++ {
        for j := i + 1; j < len(ls); j++ {
            if ls[i] < ls[j] {
                ls[i], ls[j] = ls[j], ls[i]
            }
        }
    }

    return ls
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"e", "f", "j", "x", "r", "k"}, []string{"a", "v", "2", "im", "nb", "vj", "z"}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
