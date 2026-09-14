package f_test

import (
    "fmt"
    "strings"
    "testing"
)

func f(array []string) string {
    if len(array) == 1 {
        return array[0]
    }

    result := make([]string, len(array)*2)
    copy(result, array)
    i := 0
    for i < len(array)-1 {
        for j := 0; j < 2; j++ {
            result[i*2] = array[i]
            i++
        }
    }
    return strings.Join(result, "")
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"ac8", "qk6", "9wg"}), expected: "ac8qk6qk6" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
