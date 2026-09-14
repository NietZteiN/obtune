package main

import (
    "fmt"
    "testing"
)

func main() {
	myString := "Hello, World!"
	encryption := 1
	result := f(myString, encryption)
	fmt.Println(result)
}

func f(myString string, encryption int) string {
	if encryption == 0 {
		return myString
	} else {
		return rot13(myString)
	}
}

func rot13(s string) string {
	var result string
	for _, char := range s {
		switch {
		case char >= 'A' && char <= 'Z':
			result += string((char-'A'+13)%26 + 'A')
		case char >= 'a' && char <= 'z':
			result += string((char-'a'+13)%26 + 'a')
		default:
			result += string(char)
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
     { actual: candidate("UppEr", 0), expected: "UppEr" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
