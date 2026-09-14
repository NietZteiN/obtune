package f_test

import (
    "testing"
    "fmt"
)

func f(d map[int]string) map[int]string {
    r := make(map[int]string)
    for len(d) > 0 {
        for k, v := range d {
            r[k] = v
        }
        maxKey := 0
        for k := range d {
            if k > maxKey {
                maxKey = k
            }
        }
        delete(d, maxKey)
    }
    return r
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]string{3: "A3", 1: "A1", 2: "A2"}), expected: map[int]string{3: "A3", 1: "A1", 2: "A2"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
