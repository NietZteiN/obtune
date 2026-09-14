package f_test

import (
    "testing"
    "fmt"
)

func f(chemicals []string, num int) []string {
    fish := make([]string, len(chemicals)-1)
    copy(fish, chemicals[1:])
    for i, j := 0, len(chemicals)-1; i < j; i, j = i+1, j-1 {
        chemicals[i], chemicals[j] = chemicals[j], chemicals[i]
    }
    for i := 0; i < num; i++ {
        fish = append(fish, chemicals[1])
        chemicals = append(chemicals[:1], chemicals[2:]...)
    }
    for i, j := 0, len(chemicals)-1; i < j; i, j = i+1, j-1 {
        chemicals[i], chemicals[j] = chemicals[j], chemicals[i]
    }
    return chemicals
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"lsi", "s", "t", "t", "d"}, 0), expected: []string{"lsi", "s", "t", "t", "d"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
