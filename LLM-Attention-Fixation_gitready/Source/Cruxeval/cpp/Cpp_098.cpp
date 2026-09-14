#include<assert.h>
#include<bits/stdc++.h>
long f(std::string s) {
    std::stringstream ss(s);
    std::string word;
    long count = 0;
    while (ss >> word) {
        if (std::isupper(word[0]) && std::all_of(word.begin() + 1, word.end(), ::islower)) 
            ++count;
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("SOME OF THIS Is uknowN!")) == (1));
}
