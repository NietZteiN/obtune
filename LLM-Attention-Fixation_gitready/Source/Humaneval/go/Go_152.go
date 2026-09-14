import (
    "math"
)

// I think we all remember that feeling when the result of some long-awaited
// event is finally known. The feelings and thoughts you have at that moment are
// definitely worth noting down and comparing.
// Your task is to determine if a person correctly guessed the results of a number of matches.
// You are given two arrays of scores and guesses of equal length, where each index shows a match.
// Return an array of the same length denoting how far off each guess was. If they have guessed correctly,
// the value is 0, and if not, the value is the absolute difference between the guess and the score.
// 
// 
// example:
// 
// Compare([1,2,3,4,5,1],[1,2,3,4,2,-2]) -> [0,0,0,0,3,3]
// Compare([0,5,0,0,0,4],[4,1,1,0,0,-2]) -> [4,4,1,0,0,6]
func Compare(game,guess []int) []int {

    ans := make([]int, 0, len(game))
    for i := range game {
        ans = append(ans, int(math.Abs(float64(game[i]-guess[i]))))
    }
    return ans
}

func TestCompare(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]int{0,0,0,0,3,3}, Compare([]int{1,2,3,4,5,1}, []int{1,2,3,4,2,-2}))
    assert.Equal([]int{4,4,1,0,0,6}, Compare([]int{0,5,0,0,0,4}, []int{4,1,1,0,0,-2}))
    assert.Equal([]int{0,0,0,0,3,3}, Compare([]int{1,2,3,4,5,1}, []int{1,2,3,4,2,-2}))
    assert.Equal([]int{0,0,0,0,0,0}, Compare([]int{0,0,0,0,0,0}, []int{0,0,0,0,0,0}))
    assert.Equal([]int{2,4,6}, Compare([]int{1,2,3}, []int{-1,-2,-3}))
    assert.Equal([]int{2,0,0,1}, Compare([]int{1,2,3,5}, []int{-1,2,3,4}))
}
