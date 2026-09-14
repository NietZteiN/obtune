#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string splitter) {
    std::transform(text.begin(), text.end(), text.begin(), ::tolower);
    std::stringstream ss(text);
    std::vector<std::string> words;
    std::string word;
    while (ss >> word) {
        words.push_back(word);
    }
    return std::accumulate(words.begin(), words.end(), std::string(""), [&splitter](const std::string& result, const std::string& word) {
        return result.empty() ? word : result + splitter + word;
    });
}
int main() {
    auto candidate = f;
    assert(candidate(("LlTHH sAfLAPkPhtsWP"), ("#")) == ("llthh#saflapkphtswp"));
}
