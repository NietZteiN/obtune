package f_test

import (
    "testing"
    "fmt"
)

func f(n int, l []string) map[int]int {
    archive := make(map[int]int)
    for i := 0; i < n; i++ {
        archive = make(map[int]int)
        for _, val := range l {
            x := 0
            fmt.Sscanf(val, "%d", &x)
            archive[x+10] = x * 10
        }
    }
    return archive
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(0, []string{"aaa", "bbb"}), expected: map[int]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
