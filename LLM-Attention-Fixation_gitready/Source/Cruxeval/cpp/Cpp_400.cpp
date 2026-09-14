#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string multi_string) {
    std::vector<std::string> words;
    std::stringstream ss(multi_string);
    std::string word;
    
    while (ss >> word) {
        bool is_ascii = true;
        for (char c : word) {
            if (c > 127) {
                is_ascii = false;
                break;
            }
        }
        if (is_ascii) {
            words.push_back(word);
        }
    }

    if (!words.empty()) {
        return std::accumulate(std::begin(words), std::end(words), std::string(),
            [](const std::string &a, const std::string &b) -> std::string { return a + (a.length() > 0 ? ", " : "") + b; });
    } else {
        return "";
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("I am hungry! eat food.")) == ("I, am, hungry!, eat, food."));
}
