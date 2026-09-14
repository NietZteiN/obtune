package f_test

import (
    "testing"
    "fmt"
)

func f(strings []string) []string {
    var newStrings []string
    for _, str := range strings {
        firstTwo := str
        if len(str) > 2 {
            firstTwo = str[:2]
        }
        if len(firstTwo) > 0 && (firstTwo[0] == 'a' || firstTwo[0] == 'p') {
            newStrings = append(newStrings, firstTwo)
        }
    }
    return newStrings
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"a", "b", "car", "d"}), expected: []string{"a"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
