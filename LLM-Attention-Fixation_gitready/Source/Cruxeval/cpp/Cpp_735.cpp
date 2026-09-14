#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string sentence) {
    if (sentence == "") {
        return "";
    }
    sentence.erase(std::remove(sentence.begin(), sentence.end(), '('), sentence.end());
    sentence.erase(std::remove(sentence.begin(), sentence.end(), ')'), sentence.end());
    std::transform(sentence.begin(), sentence.end(), sentence.begin(), ::tolower);
    sentence[0] = std::toupper(sentence[0]);
    sentence.erase(std::remove(sentence.begin(), sentence.end(), ' '), sentence.end());
    return sentence;
}
int main() {
    auto candidate = f;
    assert(candidate(("(A (b B))")) == ("Abb"));
}
