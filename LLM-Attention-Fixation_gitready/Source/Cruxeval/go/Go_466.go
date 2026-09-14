package main

import (
    "fmt"
    "testing"
)

func f(text string) string {
	length := len(text)
	index := 0
	for index < length && text[index] == ' ' {
		index++
	}
	endIndex := index + 5
	if endIndex > length {
		endIndex = length
	}
	return text[index:endIndex]
}

func main() {
	text := "   Hello, World!"
	result := f(text)
	fmt.Println(result)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("-----	\n	th\n-----"), expected: "-----" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
