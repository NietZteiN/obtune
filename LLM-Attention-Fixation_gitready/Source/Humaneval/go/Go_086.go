import (
    "sort"
    "strings"
)

// Write a function that takes a string and returns an ordered version of it.
// Ordered version of string, is a string where all words (separated by space)
// are replaced by a new word where all the characters arranged in
// ascending order based on ascii value.
// Note: You should keep the order of words and blank spaces in the sentence.
// 
// For example:
// AntiShuffle('Hi') returns 'Hi'
// AntiShuffle('hello') returns 'ehllo'
// AntiShuffle('Hello World!!!') returns 'Hello !!!Wdlor'
func AntiShuffle(s string) string {

    strs := make([]string, 0)
    for _, i := range strings.Fields(s) {
        word := []rune(i)
        sort.Slice(word, func(i, j int) bool {
            return word[i] < word[j]
        })
        strs = append(strs, string(word))
    }
    return strings.Join(strs, " ")
}

func TestAntiShuffle(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("Hi", AntiShuffle("Hi"))
    assert.Equal("ehllo", AntiShuffle("hello"))
    assert.Equal("bemnru", AntiShuffle("number"))
    assert.Equal("abcd", AntiShuffle("abcd"))
    assert.Equal("Hello !!!Wdlor", AntiShuffle("Hello World!!!"))
    assert.Equal("", AntiShuffle(""))
    assert.Equal(".Hi My aemn is Meirst .Rboot How aer ?ouy", AntiShuffle("Hi. My name is Mister Robot. How are you?"))
}
