import (
    "strings"
)

// You are given a string representing a sentence,
// the sentence contains some words separated by a space,
// and you have to return a string that contains the words from the original sentence,
// whose lengths are prime numbers,
// the order of the words in the new string should be the same as the original one.
// 
// Example 1:
// Input: sentence = "This is a test"
// Output: "is"
// 
// Example 2:
// Input: sentence = "lets go for swimming"
// Output: "go for"
// 
// Constraints:
// * 1 <= len(sentence) <= 100
// * sentence contains only letters
func WordsInSentence(sentence string) string {

    new_lst := make([]string, 0)
    for _, word := range strings.Fields(sentence) {
        flg := 0
        if len(word) == 1 {
            flg = 1
        }
        for i := 2;i < len(word);i++ {
            if len(word)%i == 0 {
                flg = 1
            }
        }
        if flg == 0 || len(word) == 2 {
            new_lst = append(new_lst, word)
        }
    }
    return strings.Join(new_lst, " ")
}

func TestWordsInSentence(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("is", WordsInSentence("This is a test"))
    assert.Equal("go for", WordsInSentence("lets go for swimming"))
    assert.Equal("there is no place", WordsInSentence("there is no place available here"))
    assert.Equal("Hi am Hussein", WordsInSentence("Hi I am Hussein"))
    assert.Equal("go for it", WordsInSentence("go for it"))
    assert.Equal("", WordsInSentence("here"))
    assert.Equal("is", WordsInSentence("here is"))
}
