import (
    "regexp"
)

// You'll be given a string of words, and your task is to count the number
// of boredoms. A boredom is a sentence that starts with the word "I".
// Sentences are delimited by '.', '?' or '!'.
// 
// For example:
// >>> IsBored("Hello world")
// 0
// >>> IsBored("The sky is blue. The sun is shining. I love this weather")
// 1
func IsBored(S string) int {

    r, _ := regexp.Compile(`[.?!]\s*`)
    sentences := r.Split(S, -1)
    sum := 0
    for _, s := range sentences {
        if len(s) >= 2 && s[:2] == "I " {
            sum++
        }
    }
    return sum
}

func TestIsBored(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(0, IsBored("Hello world"), "Test 1")
    assert.Equal(0, IsBored("Is the sky blue?"), "Test 2")
    assert.Equal(1, IsBored("I love It !"), "Test 3")
    assert.Equal(0, IsBored("bIt"), "Test 4")
    assert.Equal(2, IsBored("I feel good today. I will be productive. will kill It"), "Test 5")
    assert.Equal(0, IsBored("You and I are going for a walk"), "Test 6")
}
