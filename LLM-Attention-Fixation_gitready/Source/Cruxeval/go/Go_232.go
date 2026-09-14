package f_test

import (
    "testing"
    "fmt"
)

func f(text string, changes string) string {
    result := ""
    count := 0
    changesList := []rune(changes)
    for _, char := range text {
        if string(char) == "e" {
            result += string(char)
        } else {
            result += string(changesList[count%len(changesList)])
        }
        if string(char) != "e" {
            count++
        }
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
     { actual: candidate("fssnvd", "yes"), expected: "yesyes" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
