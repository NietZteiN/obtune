package f_test

import (
    "fmt"
    "strings"
    "testing"
)

func f(ints []int) string {
    counts := make([]int, 301)

    for _, i := range ints {
        counts[i]++
    }

    var r []string
    for i, count := range counts {
        if count >= 3 {
            r = append(r, fmt.Sprint(i))
        }
    }
    counts = nil
    return strings.Join(r, " ")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{2, 3, 5, 2, 4, 5, 2, 89}), expected: "2" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
