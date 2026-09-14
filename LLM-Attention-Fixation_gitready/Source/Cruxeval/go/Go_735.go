package f_test

import (
	"strings"
	"testing"
	"fmt"
)

func f(sentence string) string {
	if sentence == "" {
		return ""
	}
	sentence = strings.ReplaceAll(sentence, "(", "")
	sentence = strings.ReplaceAll(sentence, ")", "")
	sentence = strings.ToUpper(string(sentence[0])) + strings.ToLower(sentence[1:])
	sentence = strings.ReplaceAll(sentence, " ", "")
	return sentence
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("(A (b B))"), expected: "Abb" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
