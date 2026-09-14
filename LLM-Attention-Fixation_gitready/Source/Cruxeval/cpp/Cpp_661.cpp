#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string letters, long maxsplit) {
    std::vector<std::string> words;
    std::string word;
    std::stringstream ss(letters);
    while (ss >> word) {
        words.push_back(word);
    }
    if (maxsplit < words.size()) {
        words.erase(words.begin(), words.end() - maxsplit);
    }
    std::string result = "";
    for (const auto &word : words) {
        result += word;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("elrts,SS ee"), (6)) == ("elrts,SSee"));
}
