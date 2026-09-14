#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::istringstream iss(text);
    std::vector<std::string> words;
    std::string word;
    while (iss >> word) {
        words.push_back(word);
    }
    
    std::string result;
    for (const std::string& w : words) {
        result += w + " ";
    }
    
    result.pop_back(); // Remove the extra space at the end
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("pvtso")) == ("pvtso"));
}
