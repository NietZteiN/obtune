package f_test

import (
	"testing"
	"fmt"
	"strconv"
)

func f(a map[int]string) string {
    s := make(map[int]string, len(a))
    keys := make([]int, 0, len(a))
    for k := range a {
        keys = append(keys, k)
    }
    for i := len(keys) - 1; i >= 0; i-- {
        s[keys[i]] = a[keys[i]]
    }
    output := ""
    for k, v := range s {
        output += "(" + strconv.Itoa(k) + ", '" + v + "') "
    }
    return output[:len(output)-1] // removing trailing space
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]string{15: "Qltuf", 12: "Rwrepny"}), expected: "(12, 'Rwrepny') (15, 'Qltuf')" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
