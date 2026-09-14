#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string strs) {
    std::vector<std::string> words;
    std::stringstream ss(strs);
    std::string word;
    while (ss >> word) {
        words.push_back(word);
    }
    for (size_t i = 1; i < words.size(); i += 2) {
        std::reverse(words[i].begin(), words[i].end());
    }
    std::string result;
    for (const auto &word : words) {
        result += word + " ";
    }
    result.pop_back();  // Remove the trailing space
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("K zBK")) == ("K KBz"));
}
