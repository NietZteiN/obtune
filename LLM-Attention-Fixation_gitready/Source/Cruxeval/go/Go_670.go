package f_test

import (
    "testing"
    "fmt"
    "sort"
)

func f(a []string, b []int) []int {
    d := make(map[string]int)
    for i, v := range a {
        d[v] = b[i]
    }
    sort.Slice(a, func(i, j int) bool {
        return d[a[i]] > d[a[j]]
    })
    result := make([]int, len(a))
    for i, v := range a {
        result[i] = d[v]
        delete(d, v)
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
     { actual: candidate([]string{"12", "ab"}, []int{2, 2}), expected: []int{2, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
