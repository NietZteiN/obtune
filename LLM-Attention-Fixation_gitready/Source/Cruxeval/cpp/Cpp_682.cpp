#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long length, long index) {
    std::stringstream ss(text);
    std::string word;
    std::vector<std::string> words;
    while (std::getline(ss, word, ' ')) {
        words.push_back(word);
    }
    std::reverse(words.begin(), words.end());
    std::string result;
    for (int i = 0; i < index && i < words.size(); ++i) {
        result += words[i].substr(0, length);
        if (i < index - 1 && i < words.size() - 1) {
            result += "_";
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("hypernimovichyp"), (2), (2)) == ("hy"));
}
