package f_test

import (
	"strconv"
	"testing"
	"fmt"
)

func f(text string, lower string, upper string) []interface{} {
    count := 0
    new_text := ""
    for _, char := range text {
        if _, err := strconv.Atoi(string(char)); err == nil {
            new_text += lower
            if string(lower) == "p" || string(lower) == "C" {
                count += 1
            }
        } else {
            new_text += upper
            if string(upper) == "p" || string(upper) == "C" {
                count += 1
            }
        }
    }
    return []interface{}{count, new_text}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("DSUWeqExTQdCMGpqur", "a", "x"), expected: []interface{}{0, "xxxxxxxxxxxxxxxxxx"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
